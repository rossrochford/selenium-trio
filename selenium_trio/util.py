
from selenium.common.exceptions import WebDriverException
import trio

from selenium_trio.extras.javascript.js_scripts import PAGE_HEIGHT_JS

WINDOW_WIDTH = 1300


async def get_page_height(driver):
    val = await driver.execute_script2(PAGE_HEIGHT_JS)
    return int(round(val))


async def scroll_to(driver, position):
    await driver.execute_script2("window.scrollTo(0, %s);" % position)


async def resize_driver(driver, initial_delay=None):

    if initial_delay:
        await trio.sleep(initial_delay)

    page_height = await get_page_height(driver)
    resize_count = 0
    while True:
        pos = await get_page_height(driver) - 600
        await scroll_to(driver, pos)
        await trio.sleep(0.7)
        new_page_height = await get_page_height(driver)
        if new_page_height == page_height or resize_count > 7:
            page_height = new_page_height
            break
        resize_count += 1
        print('--- EXPANDING PAGE_HEIGHT ---')

    await scroll_to(driver, 0)
    await trio.sleep(0.1)

    window_height = page_height + 120

    await driver.set_window_size2(WINDOW_WIDTH, window_height)
    await trio.sleep(0.25)  # need to do it twice sometimes
    await driver.set_window_size2(WINDOW_WIDTH, window_height)


# RelativeBy wasn't importing successfully so it's copied here.
# For original see: selenium.webdriver.support.relative_locator.RelativeBy
class RelativeBy(object):

    def __init__(self, root=None, filters=None):
        self.root = root
        self.filters = filters or []

    def above(self, element_or_locator=None):
        if element_or_locator is None:
            raise WebDriverException("Element or locator must be given when calling above method")

        self.filters.append({"kind": "above", "args": [element_or_locator]})
        return self

    def below(self, element_or_locator=None):
        if element_or_locator is None:
            raise WebDriverException("Element or locator must be given when calling above method")

        self.filters.append({"kind": "below", "args": [element_or_locator]})
        return self

    def to_left_of(self, element_or_locator=None):
        if element_or_locator is None:
            raise WebDriverException("Element or locator must be given when calling above method")

        self.filters.append({"kind": "left", "args": [element_or_locator]})
        return self

    def to_right_of(self, element_or_locator):
        if element_or_locator is None:
            raise WebDriverException("Element or locator must be given when calling above method")

        self.filters.append({"kind": "right", "args": [element_or_locator]})
        return self

    def near(self, element_or_locator_distance=None):
        if element_or_locator_distance is None:
            raise WebDriverException("Element or locator or distance must be given when calling above method")

        self.filters.append({"kind": "near", "args": [element_or_locator_distance]})
        return self

    def to_dict(self):
        return {
            'relative': {
                'root': self.root,
                'filters': self.filters,
            }
        }
