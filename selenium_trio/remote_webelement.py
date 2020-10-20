from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import getAttribute_js
from selenium.webdriver.remote.webelement import isDisplayed_js

from selenium_trio.extras.async_property.base import async_property


SUBMIT_SCRIPT = """
var e = arguments[0].ownerDocument.createEvent('Event');
e.initEvent('submit', true, true);
if (arguments[0].dispatchEvent(e)) { arguments[0].submit() }
"""


class AsyncRemoteWebElement(object):
    # original superclass: selenium.webdriver.remote.webelement.WebElement
    def __init__(self, parent, id_, w3c=False):
        assert w3c is True
        self._parent = parent
        self._id = id_
        self._w3c = w3c

    def __repr__(self):
        return '<{0.__module__}.{0.__name__} (session="{1}", element="{2}")>'.format(
            type(self), self._parent.session_id, self._id
        )

    @async_property
    async def text2(self):
        result = await self._execute2(Command.GET_ELEMENT_TEXT)
        return result['value']

    @async_property
    async def tag_name(self):
        result = await self._execute2(Command.GET_ELEMENT_TAG_NAME)
        return result['value']

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id

    async def _execute2(self, command, params=None):
        # Executes a command against the underlying HTML element.
        if not params:
            params = {}
        params['id'] = self._id
        return await self._parent.execute2(command, params)

    async def get_property2(self, name):
        try:
            result = await self._execute2(Command.GET_ELEMENT_PROPERTY, {"name": name})
            return result["value"]
        except WebDriverException:
            # if we hit an end point that doesnt understand getElementProperty lets fake it
            p = self.parent
            return await p.execute_script2('return arguments[0][arguments[1]]', self, name)

    async def get_attribute2(self, name):
        script = "return (%s).apply(null, arguments);" % getAttribute_js
        return await self.parent.execute_script2(script, self, name)

    async def is_displayed2(self):
        return await self.parent.execute_script2("return (%s).apply(null, arguments);" % isDisplayed_js, self)

    async def find_elements_by_xpath2(self, xpath):
        return await self.find_elements2(by=By.XPATH, value=xpath)

    async def find_elements2(self, by=By.ID, value=None):
        if self._w3c:
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

        result = await self._execute2(Command.FIND_CHILD_ELEMENTS, {"using": by, "value": value})
        return result['value']

    async def send_keys2(self, keys_str):
        value = (keys_str,)
        # setting file inputs is not yet supported, here is the old code:
        '''
        if self.parent._is_remote:
            local_file = self.parent.file_detector.is_local_file(*value)
            if local_file is not None:
                value = self._upload(local_file)
        '''
        di = {
            'text': "".join(keys_to_typing(value)),
            'value': keys_to_typing(value)
        }
        await self._execute2(Command.SEND_KEYS_TO_ELEMENT, di)

    async def click2(self):
        await self._execute2(Command.CLICK_ELEMENT)

    async def submit2(self):
        form = await self.find_element2(By.XPATH, "./ancestor-or-self::form")
        await self._parent.execute_script2(SUBMIT_SCRIPT, form)

    async def value_of_css_property2(self, property_name):
        result = await self._execute2(
            Command.GET_ELEMENT_VALUE_OF_CSS_PROPERTY, {'propertyName': property_name}
        )
        return result['value']

    @async_property
    async def rect2(self):
        result = await self._execute2(Command.GET_ELEMENT_RECT)
        return result['value']

    async def find_elements_by_tag_name2(self, name):
        return await self.find_elements2(by=By.TAG_NAME, value=name)

