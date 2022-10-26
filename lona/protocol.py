from __future__ import annotations

from typing import Union, Dict, Any
from enum import Enum
import json

from lona._json import dumps

NoneType = type(None)


class PROTOCOL(Enum):
    MESSAGE_PREFIX = 'lona:'


class EXIT_CODE(Enum):
    SUCCESS = 0
    INVALID_MESSAGE = 1
    INVALID_METHOD = 2


class METHOD(Enum):
    # issuer: client
    VIEW = 101
    INPUT_EVENT = 102
    INPUT_EVENT_ACK = 103
    CLIENT_ERROR = 104
    PING = 105

    # issuer: server
    REDIRECT = 201
    HTTP_REDIRECT = 202
    DATA = 203
    VIEW_START = 204
    VIEW_STOP = 205
    PONG = 206


class INPUT_EVENT_TYPE(Enum):
    CLICK = 301
    CHANGE = 302
    CUSTOM = 303
    FOCUS = 304
    BLUR = 305


class NODE_TYPE(Enum):
    NODE = 401
    TEXT_NODE = 402
    WIDGET = 403


class DATA_TYPE(Enum):
    HTML = 501
    HTML_TREE = 502
    HTML_UPDATE = 503


class PATCH_TYPE(Enum):
    ID_LIST = 601
    CLASS_LIST = 602
    STYLE = 603
    ATTRIBUTES = 604
    NODES = 605
    WIDGET_DATA = 606


class OPERATION(Enum):
    SET = 701
    RESET = 702
    ADD = 703
    CLEAR = 704
    INSERT = 705
    REMOVE = 706


ENUMS = [
    PROTOCOL,
    EXIT_CODE,
    METHOD,
    INPUT_EVENT_TYPE,
    NODE_TYPE,
    DATA_TYPE,
    PATCH_TYPE,
    OPERATION,
]


def get_enum_values() -> Dict[str, Dict[str, Any]]:
    enums = {}

    for enum in ENUMS:
        enum_values = {}

        for enum_value in enum:
            enum_values[enum_value.name] = enum_value.value

        enums[enum.__name__] = enum_values

    return enums


def decode_message(raw_message: str) -> tuple[
    EXIT_CODE,
    None | int,
    None | int,
    None | int,
    Union[
        None,
        tuple[str, None | dict],
        tuple[int, int | str],
        tuple[str, None],
    ],
]:
    """
    returns: (exit_code, window_id, view_runtime_id, method, payload)

    """

    def _invalid_message() -> tuple[EXIT_CODE, None, None, None, None]:
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

    window_id, view_runtime_id, method, payload = message

    try:
        method = METHOD(method)
        message[2] = method

    except ValueError:
        return _invalid_message()

    if method != METHOD.PING:
        # window_id
        if not isinstance(message[0], int):
            return _invalid_message()

        # view_runtime_id
        if not isinstance(message[1], (str, NoneType)):
            return _invalid_message()

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
        if isinstance(payload[1], int):
            try:
                payload[1] = INPUT_EVENT_TYPE(payload[1])

            except ValueError:
                return _invalid_message()

        elif not isinstance(payload[1], str):
            return _invalid_message()

        return (EXIT_CODE.SUCCESS, *message)

    # client error
    if method == METHOD.CLIENT_ERROR:
        if not isinstance(payload[0], str):
            return _invalid_message()

        return (EXIT_CODE.SUCCESS, *message)

    # ping
    if method == METHOD.PING:
        if (window_id is not None or
                view_runtime_id is not None or
                payload is not None):

            return _invalid_message()

        return (EXIT_CODE.SUCCESS, None, None, METHOD.PING, None)

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


def encode_pong():
    return PROTOCOL.MESSAGE_PREFIX.value + dumps(
        [None, None, METHOD.PONG, None],
    )
