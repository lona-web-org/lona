import json

from lona.types import Symbol
from lona.json import dumps

NoneType = type(None)


class PROTOCOL(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    MESSAGE_PREFIX = Symbol('MESSAGE_PREFIX', 'lona:')


class EXIT_CODE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    SUCCESS = Symbol('SUCCESS', 0)
    INVALID_MESSAGE = Symbol('INVALID_MESSAGE', 1)
    INVALID_METHOD = Symbol('INVALID_METHOD', 2)


class METHOD(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    VIEW = Symbol('VIEW', 101)
    INPUT_EVENT = Symbol('INPUT_EVENT', 102)
    INPUT_EVENT_ACK = Symbol('INPUT_EVENT_ACK', 201)
    REDIRECT = Symbol('REDIRECT', 202)
    HTTP_REDIRECT = Symbol('HTTP_REDIRECT', 203)
    DATA = Symbol('DATA', 204)
    VIEW_START = Symbol('VIEW_START', 205)
    VIEW_STOP = Symbol('VIEW_STOP', 206)


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


class PATCH_TYPE(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    ID_LIST = Symbol('ID_LIST', 601)
    CLASS_LIST = Symbol('CLASS_LIST', 602)
    STYLE = Symbol('STYLE', 603)
    ATTRIBUTES = Symbol('ATTRIBUTES', 604)
    NODES = Symbol('NODES', 605)
    WIDGET_DATA = Symbol('WIDGET_DATA', 606)


class OPERATION(Symbol):
    _INCLUDE_IN_FRONTEND_LIBRARY = True

    SET = Symbol('SET', 701)
    RESET = Symbol('RESET', 702)
    ADD = Symbol('ADD', 703)
    CLEAR = Symbol('CLEAR', 704)
    INSERT = Symbol('INSERT', 705)
    REMOVE = Symbol('REMOVE', 706)


def decode_message(raw_message):
    """
    returns: (exit_code, window_id, view_runtime_id, method, payload)

    """

    def _invalid_message():
        return EXIT_CODE.INVALID_MESSAGE, None, None, None, None

    if not raw_message.startswith(PROTOCOL.MESSAGE_PREFIX.value):
        return _invalid_message()

    message = raw_message[len(PROTOCOL.MESSAGE_PREFIX.value):]

    try:
        message = json.loads(message)

    except json.JSONDecodeError:
        return _invalid_message()

    if not isinstance(message, list):
        return _invalid_message()

    if len(message) != 4:
        return _invalid_message()

    # window_id
    if not isinstance(message[0], int):
        return _invalid_message()

    # view_runtime_id
    if not isinstance(message[1], (str, NoneType)):
        return _invalid_message()

    window_id, view_runtime_id, method, payload = message

    # view
    if method == METHOD.VIEW:
        if not isinstance(payload[0], str):
            return _invalid_message()

        if not isinstance(payload[1], (dict, NoneType)):
            return _invalid_message()

        return (EXIT_CODE.SUCCESS, *message)

    # input event
    if method == METHOD.INPUT_EVENT:

        # event id
        if not isinstance(payload[0], int):
            return _invalid_message()

        # event type
        if not (isinstance(payload[1], str) or 304 > payload[1] > 300):
            return _invalid_message()

        return (EXIT_CODE.SUCCESS, *message)

    return (EXIT_CODE.INVALID_METHOD, *message)


def encode_input_event_ack(window_id, view_runtime_id, input_event_id):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.INPUT_EVENT_ACK, input_event_id],
    )


def encode_redirect(window_id, view_runtime_id, target_url):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.REDIRECT, target_url],
    )


def encode_http_redirect(window_id, view_runtime_id, target_url):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.HTTP_REDIRECT, target_url],
    )


def encode_data(window_id, view_runtime_id, title, data):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.DATA, [title, data]],
    )


def encode_view_start(window_id, view_runtime_id):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.VIEW_START, None],
    )


def encode_view_stop(window_id, view_runtime_id):
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [window_id, view_runtime_id, METHOD.VIEW_STOP, None],
    )
