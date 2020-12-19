from lona.types import Symbol


class EXIT_CODE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    SUCCESS = Symbol('SUCCESS', 0)
    INVALID_MESSAGE = Symbol('INVALID_MESSAGE', 1)
    INVALID_METHOD = Symbol('INVALID_METHOD', 2)


class METHOD(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    VIEW = Symbol('VIEW', 101)
    INPUT_EVENT = Symbol('INPUT_EVENT', 102)
    REDIRECT = Symbol('REDIRECT', 201)
    HTTP_REDIRECT = Symbol('HTTP_REDIRECT', 202)
    DATA = Symbol('DATA', 203)
    VIEW_START = Symbol('VIEW_START', 204)
    VIEW_STOP = Symbol('VIEW_STOP', 205)


class INPUT_EVENT_TYPE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    CLICK = Symbol('CLICK', 301)
    CHANGE = Symbol('CHANGE', 302)
    SUBMIT = Symbol('SUBMIT', 303)
    CUSTOM = Symbol('CUSTOM', 304)


class NODE_TYPE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    NODE = Symbol('NODE', 401)
    TEXT_NODE = Symbol('TEXT_NODE', 402)
    WIDGET = Symbol('WIDGET', 403)


class DATA_TYPE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    HTML = Symbol('HTML', 501)
    HTML_TREE = Symbol('HTML_TREE', 502)
    HTML_UPDATE = Symbol('HTML_UPDATE', 503)


class OPERATION(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    SET = Symbol('SET', 601)
    RESET = Symbol('RESET', 602)
    ADD = Symbol('ADD', 603)
    CLEAR = Symbol('CLEAR', 604)
    INSERT = Symbol('INSERT', 605)
    REMOVE = Symbol('REMOVE', 606)


def decode_message(message):
    """
    returns: (exit_code, window_id, method, url, payload)

    """

    if not isinstance(message, list):
        return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

    if not isinstance(message[0], int):
        return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

    # view
    if message[1] == METHOD.VIEW:
        if not isinstance(message[2], str):
            return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

        payload = None

        if len(message) > 3:
            payload = message[3]

        return EXIT_CODE.SUCCESS, message[0], METHOD.VIEW, message[2], payload

    # input event
    if message[1] == METHOD.INPUT_EVENT:
        if not isinstance(message[2], str):
            return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

        if not (isinstance(message[3], str) or 304 > message[3] > 300):
            return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

        return (EXIT_CODE.SUCCESS, message[0], METHOD.INPUT_EVENT,
                message[2], message[3:])

    return EXIT_CODE.INVALID_MESSAGE, None, None, None, None


def encode_redirect(window_id, url, target_url):
    return [window_id, METHOD.REDIRECT, url, target_url]


def encode_http_redirect(window_id, url, target_url):
    return [window_id, METHOD.HTTP_REDIRECT, url, target_url]


def encode_data(window_id, url, title, data):
    return [window_id, METHOD.DATA, url, title, data]


def encode_view_start(window_id, url):
    return [window_id, METHOD.VIEW_START, url]


def encode_view_stop(window_id, url):
    return [window_id, METHOD.VIEW_STOP, url]
