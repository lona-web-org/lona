import json

from lona.types import Symbol


def dumps(data):
    def default(value):
        if isinstance(value, Symbol):
            return value.value

        raise TypeError

    return json.dumps(data, default=default)


class ExitCode(Symbol):
    SUCCESS = Symbol('SUCCESS', 0)
    INVALID_MESSAGE = Symbol('INVALID_MESSAGE', 1)
    INVALID_METHOD = Symbol('INVALID_METHOD', 2)


class Method(Symbol):
    VIEW = Symbol('VIEW', 101)
    INPUT_EVENT = Symbol('INPUT_EVENT', 102)
    REDIRECT = Symbol('REDIRECT', 201)
    HTTP_REDIRECT = Symbol('HTTP_REDIRECT', 202)
    DATA = Symbol('DATA', 203)
    VIEW_START = Symbol('VIEW_START', 204)
    VIEW_STOP = Symbol('VIEW_STOP', 205)


class InputEventType(Symbol):
    CLICK = Symbol('CLICK', 301)
    CHANGE = Symbol('CHANGE', 302)
    SUBMIT = Symbol('SUBMIT', 303)
    CUSTOM = Symbol('CUSTOM', 304)


class NodeType(Symbol):
    NODE = Symbol('NODE', 401)
    TEXT_NODE = Symbol('TEXT_NODE', 402)
    WIDGET = Symbol('WIDGET', 403)


class DataType(Symbol):
    HTML = Symbol('HTML', 501)
    HTML_TREE = Symbol('HTML_TREE', 502)
    HTML_UPDATE = Symbol('HTML_UPDATE', 503)


class Operation(Symbol):
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
        return ExitCode.INVALID_MESSAGE, None, None, None, None

    if not isinstance(message[0], int):
        return ExitCode.INVALID_MESSAGE, None, None, None, None

    # view
    if message[1] == Method.VIEW:
        if not isinstance(message[2], str):
            return ExitCode.INVALID_MESSAGE, None, None, None, None

        payload = None

        if len(message) > 3:
            payload = message[3]

        return ExitCode.SUCCESS, message[0], Method.VIEW, message[2], payload

    # input event
    if message[1] == Method.INPUT_EVENT:
        if not isinstance(message[2], str):
            return ExitCode.INVALID_MESSAGE, None, None, None, None

        if not (isinstance(message[3], str) or 304 > message[3] > 300):
            return ExitCode.INVALID_MESSAGE, None, None, None, None

        return (ExitCode.SUCCESS, message[0], Method.INPUT_EVENT,
                message[2], message[3:])

    return ExitCode.INVALID_MESSAGE, None, None, None, None


def encode_redirect(window_id, url, target_url):
    return [window_id, Method.REDIRECT, url, target_url]


def encode_http_redirect(window_id, url, target_url):
    return [window_id, Method.HTTP_REDIRECT, url, target_url]


def encode_data(window_id, url, title, html_data, widget_data):
    return [window_id, Method.DATA, url, title, html_data, widget_data]


def encode_view_start(window_id, url):
    return [window_id, Method.VIEW_START, url]


def encode_view_stop(window_id, url):
    return [window_id, Method.VIEW_STOP, url]
