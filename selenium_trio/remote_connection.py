import json
import logging
import string
import warnings
try:
    from urllib import parse
except ImportError:  # above is available in py3+, below is py2.7
    import urlparse as parse

import httpx
from selenium.webdriver.firefox.remote_connection import FirefoxRemoteConnection
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.errorhandler import ErrorCode


LOGGER = logging.getLogger(__name__)


COMMANDS = {
    Command.STATUS: ('GET', '/status'),
    Command.NEW_SESSION: ('POST', '/session'),
    Command.GET_ALL_SESSIONS: ('GET', '/sessions'),
    Command.QUIT: ('DELETE', '/session/$sessionId'),
    Command.GET_CURRENT_WINDOW_HANDLE:
        ('GET', '/session/$sessionId/window_handle'),
    Command.W3C_GET_CURRENT_WINDOW_HANDLE:
        ('GET', '/session/$sessionId/window'),
    Command.GET_WINDOW_HANDLES:
        ('GET', '/session/$sessionId/window_handles'),
    Command.W3C_GET_WINDOW_HANDLES:
        ('GET', '/session/$sessionId/window/handles'),
    Command.GET: ('POST', '/session/$sessionId/url'),
    Command.GO_FORWARD: ('POST', '/session/$sessionId/forward'),
    Command.GO_BACK: ('POST', '/session/$sessionId/back'),
    Command.REFRESH: ('POST', '/session/$sessionId/refresh'),
    Command.EXECUTE_SCRIPT: ('POST', '/session/$sessionId/execute'),
    Command.W3C_EXECUTE_SCRIPT:
        ('POST', '/session/$sessionId/execute/sync'),
    Command.W3C_EXECUTE_SCRIPT_ASYNC:
        ('POST', '/session/$sessionId/execute/async'),
    Command.GET_CURRENT_URL: ('GET', '/session/$sessionId/url'),
    Command.GET_TITLE: ('GET', '/session/$sessionId/title'),
    Command.GET_PAGE_SOURCE: ('GET', '/session/$sessionId/source'),
    Command.SCREENSHOT: ('GET', '/session/$sessionId/screenshot'),
    Command.ELEMENT_SCREENSHOT: ('GET', '/session/$sessionId/element/$id/screenshot'),
    Command.FIND_ELEMENT: ('POST', '/session/$sessionId/element'),
    Command.FIND_ELEMENTS: ('POST', '/session/$sessionId/elements'),
    Command.W3C_GET_ACTIVE_ELEMENT: ('GET', '/session/$sessionId/element/active'),
    Command.GET_ACTIVE_ELEMENT:
        ('POST', '/session/$sessionId/element/active'),
    Command.FIND_CHILD_ELEMENT:
        ('POST', '/session/$sessionId/element/$id/element'),
    Command.FIND_CHILD_ELEMENTS:
        ('POST', '/session/$sessionId/element/$id/elements'),
    Command.CLICK_ELEMENT: ('POST', '/session/$sessionId/element/$id/click'),
    Command.CLEAR_ELEMENT: ('POST', '/session/$sessionId/element/$id/clear'),
    Command.SUBMIT_ELEMENT: ('POST', '/session/$sessionId/element/$id/submit'),
    Command.GET_ELEMENT_TEXT: ('GET', '/session/$sessionId/element/$id/text'),
    Command.SEND_KEYS_TO_ELEMENT:
        ('POST', '/session/$sessionId/element/$id/value'),
    Command.SEND_KEYS_TO_ACTIVE_ELEMENT:
        ('POST', '/session/$sessionId/keys'),
    Command.UPLOAD_FILE: ('POST', "/session/$sessionId/file"),
    Command.GET_ELEMENT_VALUE:
        ('GET', '/session/$sessionId/element/$id/value'),
    Command.GET_ELEMENT_TAG_NAME:
        ('GET', '/session/$sessionId/element/$id/name'),
    Command.IS_ELEMENT_SELECTED:
        ('GET', '/session/$sessionId/element/$id/selected'),
    Command.SET_ELEMENT_SELECTED:
        ('POST', '/session/$sessionId/element/$id/selected'),
    Command.IS_ELEMENT_ENABLED:
        ('GET', '/session/$sessionId/element/$id/enabled'),
    Command.IS_ELEMENT_DISPLAYED:
        ('GET', '/session/$sessionId/element/$id/displayed'),
    Command.GET_ELEMENT_LOCATION:
        ('GET', '/session/$sessionId/element/$id/location'),
    Command.GET_ELEMENT_LOCATION_ONCE_SCROLLED_INTO_VIEW:
        ('GET', '/session/$sessionId/element/$id/location_in_view'),
    Command.GET_ELEMENT_SIZE:
        ('GET', '/session/$sessionId/element/$id/size'),
    Command.GET_ELEMENT_RECT:
        ('GET', '/session/$sessionId/element/$id/rect'),
    Command.GET_ELEMENT_ATTRIBUTE:
        ('GET', '/session/$sessionId/element/$id/attribute/$name'),
    Command.GET_ELEMENT_PROPERTY:
        ('GET', '/session/$sessionId/element/$id/property/$name'),
    Command.GET_ALL_COOKIES: ('GET', '/session/$sessionId/cookie'),
    Command.ADD_COOKIE: ('POST', '/session/$sessionId/cookie'),
    Command.GET_COOKIE: ('GET', '/session/$sessionId/cookie/$name'),
    Command.DELETE_ALL_COOKIES:
        ('DELETE', '/session/$sessionId/cookie'),
    Command.DELETE_COOKIE:
        ('DELETE', '/session/$sessionId/cookie/$name'),
    Command.SWITCH_TO_FRAME: ('POST', '/session/$sessionId/frame'),
    Command.SWITCH_TO_PARENT_FRAME: ('POST', '/session/$sessionId/frame/parent'),
    Command.SWITCH_TO_WINDOW: ('POST', '/session/$sessionId/window'),

    # Command.NEW_WINDOW
    'newWindow': ('POST', '/session/$sessionId/window/new'),

    Command.CLOSE: ('DELETE', '/session/$sessionId/window'),
    Command.GET_ELEMENT_VALUE_OF_CSS_PROPERTY:
        ('GET', '/session/$sessionId/element/$id/css/$propertyName'),
    Command.IMPLICIT_WAIT:
        ('POST', '/session/$sessionId/timeouts/implicit_wait'),
    Command.EXECUTE_ASYNC_SCRIPT: ('POST', '/session/$sessionId/execute_async'),
    Command.SET_SCRIPT_TIMEOUT:
        ('POST', '/session/$sessionId/timeouts/async_script'),
    Command.SET_TIMEOUTS:
        ('POST', '/session/$sessionId/timeouts'),

    #Command.GET_TIMEOUTS:
    'getTimeouts': ('GET', '/session/$sessionId/timeouts'),

    Command.DISMISS_ALERT:
        ('POST', '/session/$sessionId/dismiss_alert'),
    Command.W3C_DISMISS_ALERT:
        ('POST', '/session/$sessionId/alert/dismiss'),
    Command.ACCEPT_ALERT:
        ('POST', '/session/$sessionId/accept_alert'),
    Command.W3C_ACCEPT_ALERT:
        ('POST', '/session/$sessionId/alert/accept'),
    Command.SET_ALERT_VALUE:
        ('POST', '/session/$sessionId/alert_text'),
    Command.W3C_SET_ALERT_VALUE:
        ('POST', '/session/$sessionId/alert/text'),
    Command.GET_ALERT_TEXT:
        ('GET', '/session/$sessionId/alert_text'),
    Command.W3C_GET_ALERT_TEXT:
        ('GET', '/session/$sessionId/alert/text'),
    Command.SET_ALERT_CREDENTIALS:
        ('POST', '/session/$sessionId/alert/credentials'),
    Command.CLICK:
        ('POST', '/session/$sessionId/click'),
    Command.W3C_ACTIONS:
        ('POST', '/session/$sessionId/actions'),
    Command.W3C_CLEAR_ACTIONS:
        ('DELETE', '/session/$sessionId/actions'),
    Command.DOUBLE_CLICK:
        ('POST', '/session/$sessionId/doubleclick'),
    Command.MOUSE_DOWN:
        ('POST', '/session/$sessionId/buttondown'),
    Command.MOUSE_UP:
        ('POST', '/session/$sessionId/buttonup'),
    Command.MOVE_TO:
        ('POST', '/session/$sessionId/moveto'),
    Command.GET_WINDOW_SIZE:
        ('GET', '/session/$sessionId/window/$windowHandle/size'),
    Command.SET_WINDOW_SIZE:
        ('POST', '/session/$sessionId/window/$windowHandle/size'),
    Command.GET_WINDOW_POSITION:
        ('GET', '/session/$sessionId/window/$windowHandle/position'),
    Command.SET_WINDOW_POSITION:
        ('POST', '/session/$sessionId/window/$windowHandle/position'),
    Command.SET_WINDOW_RECT:
        ('POST', '/session/$sessionId/window/rect'),
    Command.GET_WINDOW_RECT:
        ('GET', '/session/$sessionId/window/rect'),
    Command.MAXIMIZE_WINDOW:
        ('POST', '/session/$sessionId/window/$windowHandle/maximize'),
    Command.W3C_MAXIMIZE_WINDOW:
        ('POST', '/session/$sessionId/window/maximize'),
    Command.SET_SCREEN_ORIENTATION:
        ('POST', '/session/$sessionId/orientation'),
    Command.GET_SCREEN_ORIENTATION:
        ('GET', '/session/$sessionId/orientation'),
    Command.SINGLE_TAP:
        ('POST', '/session/$sessionId/touch/click'),
    Command.TOUCH_DOWN:
        ('POST', '/session/$sessionId/touch/down'),
    Command.TOUCH_UP:
        ('POST', '/session/$sessionId/touch/up'),
    Command.TOUCH_MOVE:
        ('POST', '/session/$sessionId/touch/move'),
    Command.TOUCH_SCROLL:
        ('POST', '/session/$sessionId/touch/scroll'),
    Command.DOUBLE_TAP:
        ('POST', '/session/$sessionId/touch/doubleclick'),
    Command.LONG_PRESS:
        ('POST', '/session/$sessionId/touch/longclick'),
    Command.FLICK:
        ('POST', '/session/$sessionId/touch/flick'),
    Command.EXECUTE_SQL:
        ('POST', '/session/$sessionId/execute_sql'),
    Command.GET_LOCATION:
        ('GET', '/session/$sessionId/location'),
    Command.SET_LOCATION:
        ('POST', '/session/$sessionId/location'),
    Command.GET_APP_CACHE:
        ('GET', '/session/$sessionId/application_cache'),
    Command.GET_APP_CACHE_STATUS:
        ('GET', '/session/$sessionId/application_cache/status'),
    Command.CLEAR_APP_CACHE:
        ('DELETE', '/session/$sessionId/application_cache/clear'),
    Command.GET_NETWORK_CONNECTION:
        ('GET', '/session/$sessionId/network_connection'),
    Command.SET_NETWORK_CONNECTION:
        ('POST', '/session/$sessionId/network_connection'),
    Command.GET_LOCAL_STORAGE_ITEM:
        ('GET', '/session/$sessionId/local_storage/key/$key'),
    Command.REMOVE_LOCAL_STORAGE_ITEM:
        ('DELETE', '/session/$sessionId/local_storage/key/$key'),
    Command.GET_LOCAL_STORAGE_KEYS:
        ('GET', '/session/$sessionId/local_storage'),
    Command.SET_LOCAL_STORAGE_ITEM:
        ('POST', '/session/$sessionId/local_storage'),
    Command.CLEAR_LOCAL_STORAGE:
        ('DELETE', '/session/$sessionId/local_storage'),
    Command.GET_LOCAL_STORAGE_SIZE:
        ('GET', '/session/$sessionId/local_storage/size'),
    Command.GET_SESSION_STORAGE_ITEM:
        ('GET', '/session/$sessionId/session_storage/key/$key'),
    Command.REMOVE_SESSION_STORAGE_ITEM:
        ('DELETE', '/session/$sessionId/session_storage/key/$key'),
    Command.GET_SESSION_STORAGE_KEYS:
        ('GET', '/session/$sessionId/session_storage'),
    Command.SET_SESSION_STORAGE_ITEM:
        ('POST', '/session/$sessionId/session_storage'),
    Command.CLEAR_SESSION_STORAGE:
        ('DELETE', '/session/$sessionId/session_storage'),
    Command.GET_SESSION_STORAGE_SIZE:
        ('GET', '/session/$sessionId/session_storage/size'),
    Command.GET_LOG:
        ('POST', '/session/$sessionId/se/log'),
    Command.GET_AVAILABLE_LOG_TYPES:
        ('GET', '/session/$sessionId/se/log/types'),
    Command.CURRENT_CONTEXT_HANDLE:
        ('GET', '/session/$sessionId/context'),
    Command.CONTEXT_HANDLES:
        ('GET', '/session/$sessionId/contexts'),
    Command.SWITCH_TO_CONTEXT:
        ('POST', '/session/$sessionId/context'),
    Command.FULLSCREEN_WINDOW:
        ('POST', '/session/$sessionId/window/fullscreen'),
    Command.MINIMIZE_WINDOW:
        ('POST', '/session/$sessionId/window/minimize')
}


class AsyncFirefoxRemoteConnection(FirefoxRemoteConnection):

    def __init__(self, remote_server_addr, keep_alive=False, resolve_ip=None):
        if resolve_ip is not None:
            warnings.warn("'resolve_ip' option removed; now resolving is done by urllib3.", DeprecationWarning)
        assert keep_alive is True
        self.keep_alive = keep_alive
        self._url = remote_server_addr
        # removed: self._proxy_url = self._get_proxy_url()

        timeout = httpx.Timeout(12.0, connect=30.0)
        self.http_session = httpx.AsyncClient(timeout=timeout)

        # removed: self._conn = self._get_connection_manager()

        self._commands = COMMANDS

    # asynchronous code
    # -------------------------------------------------------

    async def execute2(self, command, params):
        url, command_info, data = self._execute__pre_request(command, params)
        return await self._request2(command_info[0], url, body=data)

    async def _request2(self, method, url, body=None):

        if body and method != 'POST' and method != 'PUT':
            body = None

        resp, data, statuscode = await self._do_request2(method, url, body)

        try:
            if 300 <= statuscode < 304:
                return self._request('GET', resp.headers['location'])
            data = self._process_response(resp, data, statuscode)
        finally:
            LOGGER.debug("Finished Request")
            resp.close()

        return data

    async def _do_request2(self, method, url, body=None):

        method = method.lower()
        parsed_url = parse.urlparse(url)
        headers = self.get_remote_connection_headers(parsed_url, self.keep_alive)

        if method == 'get':
            resp = await self.http_session.get(url, headers=headers)
        else:
            func = getattr(self.http_session, method)
            resp = await func(url, data=body, headers=headers)

        data = resp.text
        statuscode = resp.status_code

        return resp, data, statuscode

    # synchronous code
    # -------------------------------------------------------

    def execute(self, command, params):
        url, command_info, data = self._execute__pre_request(command, params)
        return self._request(command_info[0], url, body=data)

    def _do_request(self, method, url, body=None):
        assert self.keep_alive is True

        parsed_url = parse.urlparse(url)
        headers = self.get_remote_connection_headers(parsed_url, self.keep_alive)

        resp = self._conn.request(method, url, body=body, headers=headers)
        statuscode = resp.status

        data = resp.data.decode('UTF-8')

        return resp, data, statuscode

    def _request(self, method, url, body=None):

        if body and method != 'POST' and method != 'PUT':
            body = None

        resp, data, statuscode = self._do_request(method, url, body)

        try:
            if 300 <= statuscode < 304:
                return self._request('GET', resp.headers['location'])

            data = self._process_response(resp, data, statuscode)
        finally:
            LOGGER.debug("Finished Request")
            resp.close()

        return data

    # shared functionality between synchronous and async code
    # -------------------------------------------------------

    def _execute__pre_request(self, command, params):
        self.w3c = True
        command_info = self._commands[command]
        assert command_info is not None, 'Unrecognised command %s' % command
        path = string.Template(command_info[1]).substitute(params)
        if hasattr(self, 'w3c') and self.w3c and isinstance(params, dict) and 'sessionId' in params:
            del params['sessionId']
        data = json.dumps(params)
        url = '%s%s' % (self._url, path)
        return url, command_info, data

    def _process_response(self, resp, data, statuscode):
        if 399 < statuscode <= 500:
            return {'status': statuscode, 'value': data}

        content_type_header = resp.headers['Content-Type']

        content_type = []
        if content_type_header is not None:
            content_type = content_type_header.split(';')
        if not any([x.startswith('image/png') for x in content_type]):
            try:
                data = json.loads(data.strip())
            except ValueError:
                if 199 < statuscode < 300:
                    status = ErrorCode.SUCCESS
                else:
                    status = ErrorCode.UNKNOWN_ERROR
                return {'status': status, 'value': data.strip()}

            # Some of the drivers incorrectly return a response
            # with no 'value' field when they should return null.
            if 'value' not in data:
                data['value'] = None
            return data
        else:
            data = {'status': 0, 'value': data}
            return data
