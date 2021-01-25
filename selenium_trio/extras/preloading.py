import trio

from selenium_trio.extras.javascript.js_scripts import PRELOAD_JS

'''
JQUERY_FILE = os.path.join(
    os.environ['EVENTS_PROJECT_DOCKER_PATH'],
    'selenium_wrapper/selenium_wrapper/jquery-3.2.1.min.js'
)'''

JQUERY_FILE = '/home/ross/code/events_project/selenium_trio/selenium_trio/javascript/jquery-3.2.1.min.js'


async def add_jquery(driver):
    # from: https://gist.github.com/anhldbk/dc7a040b7fda199a5791

    async with await trio.open_file(JQUERY_FILE) as f:
        jquery = await f.read()

    await driver.execute_script2(jquery)  # active the jquery lib


async def get_multiple_outer__chunk(driver, elems):
    # old name
    return await get_multiple_outer(driver, elems)


async def get_multiple_outer(driver, elems):

    if not elems:
        return []

    # elems_unwrapped = elems
    # if type(elems[0]) in (WebElementWrapper, LinkWebElementWrapper):
    #    elems_unwrapped = [e.driver_elem for e in elems]

    script = "return (%s).apply(null, arguments);" % PRELOAD_JS['getOuterHTML_js_multiple']
    return await driver.execute_script2(script, *elems)


async def get_parent_paths_multiple(driver, elems, wrap=False):

    elems_unwrapped = elems
    #if type(elems[0]) in (WebElementWrapper, LinkWebElementWrapper):
    #    elems_unwrapped = [e.driver_elem for e in elems]

    ans = await driver.execute_script2(
        "return (%s).apply(null, arguments);" % PRELOAD_JS['get_parent_paths'],
        *elems_unwrapped
    )

    for parent_path in ans:
        # remove trailing body tag
        while parent_path and parent_path[-1]['tag_name'] in ('body', 'html'):
            del parent_path[-1]

        '''
        if wrap:
            for elem_dict in parent_path:
                e = elem_dict['elem']
                elem_dict['elem'] = WebElementWrapper.create(
                    e, driver, tag_name=elem_dict['tag_name'], outer_html=elem_dict['outer_html']
                )  
        '''

    return ans


async def get_xpaths_multiple(driver, elems):

    elems_unwrapped = elems
    # if type(elems[0]) in (WebElementWrapper, LinkWebElementWrapper):
    #    elems_unwrapped = [e.driver_elem for e in elems]

    xpaths = await driver.execute_script2(
        "return (%s).apply(null, arguments);" % PRELOAD_JS['get_xpaths'],
        *elems_unwrapped
    )
    for i, xp in enumerate(xpaths):
        xpaths[i] = '//html/' + xp

    return xpaths


async def get_rect_multiple(driver, elems):

    # todo: throws an error with: https://www.slow-journalism.com/filter/events-and-classes and: http://www.irishinbritain.org/whats-on
    # elems_unwrapped = elems
    #if type(elems[0]) in (WebElementWrapper, LinkWebElementWrapper):
    #    elems_unwrapped = [e.driver_elem for e in elems]

    script = "return (%s).apply(null, arguments);" % PRELOAD_JS['getRect_multiple_js']
    return await driver.execute_script2(script, *elems)


async def get_computed_css_multiple(driver, elems):

    elems_unwrapped = elems
    #if type(elems[0]) in (WebElementWrapper, LinkWebElementWrapper):
    #    elems_unwrapped = [e.driver_elem for e in elems]

    ans = None
    try:
        ans = await driver.execute_script2(
            "return (%s).apply(null, arguments);" % PRELOAD_JS['getComputedCss_multiple_js'],
            *elems_unwrapped
        )
    except:
        pass

    if ans:
        return ans

    if 'jquery' in driver.page_sourceL:  # todo: though we should really be testing whether $() fails
        # jquery is missing but wasn't added by preload_element_data()
        # because 'jquery' was found in page_source, so we add it and
        # try again. Usually this happens if jquery on the original page
        # failed to load
        # NOTE: assumes this is always called within or by preload_element_data()
        await add_jqeury(driver)
        ans = await driver.execute_script2(
            "return (%s).apply(null, arguments);" % PRELOAD_JS['getComputedCss_multiple_js'],
            *elems_unwrapped
        )
    if ans is None:
        import pdb; pdb.set_trace()
    return ans
