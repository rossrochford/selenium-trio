import base64
import os
import pkgutil
import tempfile
import warnings

import httpx
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

import trio

from selenium_trio.extras.async_property.base import async_property
from selenium_trio.extras.drawing import DrawingMixin
from selenium_trio.remote_connection import AsyncFirefoxRemoteConnection
from selenium_trio.remote_webelement import AsyncRemoteWebElement
from selenium_trio.util import get_page_height, scroll_to, RelativeBy


class TrioAsyncDriver(RemoteWebDriver, DrawingMixin):
    _web_element_cls = AsyncRemoteWebElement

    def __init__(
        self, command_executor='http://127.0.0.1:4444',
        desired_capabilities=None, browser_profile=None, proxy=None,
        keep_alive=True, file_detector=None, options=None, session_id=None
    ):
        assert command_executor.__class__.__name__ == 'AsyncFirefoxRemoteConnection'
        assert keep_alive is True

        super(TrioAsyncDriver, self).__init__(
            command_executor=command_executor, desired_capabilities=desired_capabilities,
            browser_profile=browser_profile, proxy=proxy, keep_alive=keep_alive,
            file_detector=file_detector, options=options
        )
        self.session_base_url = self.url = f'{command_executor._url}/session/{session_id}'
        self.session_id = session_id
        self.w3c = True

        self.canvas_added = False

    @classmethod
    async def create_local_driver(cls):

        def _create_new_driver_connection():
            driver = webdriver.Firefox()
            return driver, driver.command_executor._url

        driver_obj, command_executor_url = await trio.to_thread.run_sync(
            _create_new_driver_connection
        )
        driver = await cls.connect_to_remote(command_executor_url, driver_obj.session_id)
        # retain underlying driver object so it doesn't get garbage collected
        driver.d = driver_obj
        return driver

    @classmethod
    async def create_selenoid_driver(cls):
        host = os.environ.get('SELENOID_HUB_HOSTNAME', 'localhost')
        capabilities = {
            'platform': 'LINUX', 'browserName': 'firefox',
            'version': '', 'enableVNC': True, 'screenResolution': '1980x2000x24'
        }
        command_executor_url = 'http://' + host + ':4444/wd/hub'
        remote_driver = webdriver.Remote(
            command_executor=command_executor_url,
            desired_capabilities=capabilities,  # browser_profile=profile
        )
        driver = await TrioAsyncDriver.connect_to_remote(
            command_executor_url, remote_driver.session_id
        )

        driver.d = remote_driver  # store this so it doesn't get garbage collected
        return driver

    @classmethod
    async def connect_to_remote(cls, command_executor_url, session_id):
        capabilities = {"browserName": "firefox"}
        command_executor_obj = AsyncFirefoxRemoteConnection(command_executor_url, True)
        return TrioAsyncDriver(
            command_executor=command_executor_obj,
            desired_capabilities=capabilities, keep_alive=True,
            session_id=session_id
        )

    '''
    def execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': self.session_id}
        else:
            params['sessionId'] = self.session_id
            return super(TrioAsyncDriver, self).execute(command, params=params)
    '''

    def start_session(self, capabilities, browser_profile):
        pass  # do nothing

    async def get_page_height(self):
        return await get_page_height(self)

    async def scroll_to(self, position):
        await scroll_to(self, position)

    async def continually_scroll_to_bottom(self, num_scrolls=None):
        height_history = []

        for i in range(num_scrolls or 60):

            height = await self.get_page_height()
            height_history.append(height)

            if num_scrolls is None and len(height_history) > 3:
                h = height_history[-2]
                if abs(h - height_history[-3]) < 100 and abs(h - height_history[-1]) < 100:
                    await trio.sleep(1)
                    break

            await self.scroll_to(max(0, height - 300))
            await trio.sleep(2.5)

        await self.scroll_to(0)
        await trio.sleep(2.5)

    async def get2(self, url):
        try:
            await self.execute2(Command.GET, {'url': url})
        except httpx._exceptions.ReadTimeout:
            # retry once
            await trio.sleep(4)
            await self.execute2(Command.GET, {'url': url})

    @async_property
    async def title2(self):
        resp = await self.execute2(Command.GET_TITLE)
        return resp['value'] if resp['value'] is not None else ""

    @async_property
    async def page_source2(self):
        return (await self.execute2(Command.GET_PAGE_SOURCE))['value']

    async def quit2(self):
        try:
            await self.execute2(Command.QUIT)
        finally:
            await self.stop_client()

    async def stop_client(self):
        # called after quit(), override for custom behaviour
        pass

    async def find_elements_by_xpath2(self, xpath):
        # warning: find_elements_by_* commands are deprecated, use find_elements() instead
        return await self.find_elements2(by=By.XPATH, value=xpath)

    async def find_elements2(self, by=By.ID, value=None):
        if isinstance(by, RelativeBy):
            _pkg = '.'.join(__name__.split('.')[:-1])
            raw_function = pkgutil.get_data(_pkg, 'findElements.js').decode('utf8')
            find_element_js = "return (%s).apply(null, arguments);" % raw_function
            return await self.execute_script2(find_element_js, by.to_dict())

        if self.w3c:
            if by == By.ID:
                by = By.CSS_SELECTOR
                value = '[id="%s"]' % value
            elif by == By.TAG_NAME:
                by = By.CSS_SELECTOR
            elif by == By.CLASS_NAME:
                by = By.CSS_SELECTOR
                value = ".%s" % value
            elif by == By.NAME:
                by = By.CSS_SELECTOR
                value = '[name="%s"]' % value

        # Return empty list if driver returns null
        # See https://github.com/SeleniumHQ/selenium/issues/4555
        result = await self.execute2(Command.FIND_ELEMENTS, {'using': by, 'value': value})
        return result['value'] or []

    async def execute2(self, driver_command, params=None):
        if self.session_id is not None:
            if not params:
                params = {'sessionId': self.session_id}
            elif 'sessionId' not in params:
                params['sessionId'] = self.session_id

        params = self._wrap_value(params)
        response = await self.command_executor.execute2(driver_command, params)
        if response:
            self.error_handler.check_response(response)
            response['value'] = self._unwrap_value(
                response.get('value', None))
            return response
        # If the server doesn't send a response, assume the command was
        # a success
        return {'success': 0, 'value': None, 'sessionId': self.session_id}

    async def execute_script2(self, script, *args):
        converted_args = list(args)
        command = Command.W3C_EXECUTE_SCRIPT
        result = await self.execute2(command, {'script': script, 'args': converted_args})
        return result['value']

    async def set_window_size2(self, width, height, windowHandle='current'):
        if windowHandle != 'current':
            warnings.warn("Only 'current' window is supported for W3C compatibile browsers.")
        await self.set_window_rect2(width=int(width), height=int(height))

    async def set_window_rect2(self, x=None, y=None, width=None, height=None):
        if (x is None and y is None) and (height is None and width is None):
            raise InvalidArgumentException("x and y or height and width need values")

        rect = {"x": x, "y": y, "width": width, "height": height}
        result = await self.execute2(Command.SET_WINDOW_RECT, rect)
        return result['value']

    async def get_window_size2(self, windowHandle='current'):
        if windowHandle != 'current':
            warnings.warn("Only 'current' window is supported for W3C compatibile browsers.")
        size = await self.get_window_rect2()
        if size.get('value', None) is not None:
            size = size['value']

        return {k: size[k] for k in ('width', 'height')}

    async def get_window_rect2(self):
        result = await self.execute2(Command.GET_WINDOW_RECT)
        return result['value']

    async def get_full_document_screenshot(self):  # , quantize=False):
        # NOTE: this only seems to work when some scrolling has been done beforehand
        # otherwise you get a large blank header

        command_url = self.session_base_url + '/moz/screenshot/full'

        result = await self.command_executor._request2('GET', command_url)

        if not result['value']:
            print('warning: get_full_document_screenshot() failed')
            import pdb; pdb.set_trace()
            print('')

        png_data = base64.b64decode(result['value'].encode('ascii'))

        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        tf.write(png_data)
        tf.close()
        # if quantize:
        #     from visual_matrix_new.screenshot import quantize_image
        #     return quantize_image(tf.name)
        return tf.name


'''
async def driver_test():

    driver = await TrioAsyncDriver.create_local()

    await driver.get2('https://twitter.com/syrianinyellow')

    await trio.sleep(0.5)
    await driver.set_window_size2(1300, 1300)
    await trio.sleep(0.5)

    for i in range(3):
        height = await driver.get_page_height()
        await driver.scroll_to(max(0, height-300))
        await trio.sleep(1)

    await trio.sleep(5)
    article_elems = await driver.find_elements_by_xpath2('//article')
    article_outers = [
        await el.get_attribute2('outerHTML') for el in article_elems
    ]
    import pdb; pdb.set_trace()
    print('Loaded:', await driver.title2)

    link_elems = await driver.find_elements_by_xpath2('//a')
    for el in link_elems:
        outer = await el.get_attribute2('outerHTML')
        print(outer[:100])
        #print(await el.text2)
    import pdb; pdb.set_trace()
    print()


def create_remote_driver(host, browser='firefox', env=None):

    #SELENOID_HOST = host or '159.69.1.174'  # <- hetzner   | droplet: 'http://46.101.57.191'  # hard-coded for now

    capabilities = {
        'platform': 'LINUX', 'browserName': browser, 'version': '',
        'enableVNC': True,
        # 'javascriptEnabled': True, 'marionette': True,
        # 'profile': {  # todo: add these
        #     'browser.download.folderList': 2,
        #     'browser.download.manager.showWhenStarting': False,
        #     'browser.download.dir': '/selenium_downloads/' + randomword(7),  # todo: serviceproxy should create this directory on startup
        #     'browser.helperApps.neverAsk.saveToDisk': 'text/calendar'
        # }
    }
    if env:
        capabilities['env'] = env

    profile = webdriver.FirefoxProfile()
    #profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    #profile.set_preference('browser.download.dir', self.downloads_folder)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/calendar,text/x-vcalendar')

    remote_driver = webdriver.Remote(
        command_executor='http://' + host + ':4444/wd/hub',
        desired_capabilities=capabilities, browser_profile=profile
    )

    if wrap:
        return FirefoxDriverWrapper(driver=remote_driver, driver_type='remote')

    return remote_driver


async def driver_test2():

    host = 'localhost'
    capabilities = {
        'platform': 'LINUX', 'browserName': 'firefox',
        'version': '', 'enableVNC': True, 'screenResolution': '1980x2000x24'
    }
    command_executor_url = 'http://' + host + ':4444/wd/hub'
    remote_driver = webdriver.Remote(
        command_executor=command_executor_url,
        desired_capabilities=capabilities,  # browser_profile=profile
    )
    remote_driver.get('https://twitter.com/syrianinyellow')
    print(remote_driver.title)
    await trio.sleep(6)
    print(remote_driver.title)

    import pdb; pdb.set_trace()

    driver = await TrioAsyncDriver.connect_to_remote(
        command_executor_url, remote_driver.session_id
    )
    driver.d = remote_driver
    await driver.get2('https://twitter.com/syrianinyellow')
    print(await driver.title2)
    await trio.sleep(7)
    print(await driver.title2)
    import pdb; pdb.set_trace()
    print()


if __name__ == '__main__':
    trio.run(driver_test2)
'''
