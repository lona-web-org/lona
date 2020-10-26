import json


def dumps(data):
    def default(value):
        if isinstance(value, Value):
            return value.value

        raise TypeError

    return json.dumps(data, default=default)


class Constant:
    @classmethod
    def generate_code_book(cls):
        data = {}

        for constant_class in cls.__subclasses__():
            class_name = constant_class.__name__
            data[class_name] = {}

            for name in dir(constant_class):
                if name.startswith('_'):
                    continue

                attribute = getattr(constant_class, name)

                if not isinstance(attribute, Value):
                    continue

                data[class_name][attribute.name] = attribute.value

        return data


class Value:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return other == self.value

    def __repr__(self):
        return self.name


class ExitCode(Constant):
    SUCCESS = Value('SUCCESS', 0)
    INVALID_MESSAGE = Value('INVALID_MESSAGE', 1)
    INVALID_METHOD = Value('INVALID_METHOD', 2)


class Method(Constant):
    VIEW = Value('VIEW', 101)
    INPUT_EVENT = Value('INPUT_EVENT', 102)
    REDIRECT = Value('REDIRECT', 201)
    HTTP_REDIRECT = Value('HTTP_REDIRECT', 202)
    DATA = Value('DATA', 203)
    VIEW_START = Value('VIEW_START', 204)
    VIEW_STOP = Value('VIEW_STOP', 205)


class InputEventType(Constant):
    CLICK = Value('CLICK', 301)
    CHANGE = Value('CHANGE', 302)
    SUBMIT = Value('SUBMIT', 303)
    CUSTOM = Value('CUSTOM', 304)


class NodeType(Constant):
    NODE = Value('NODE', 401)
    TEXT_NODE = Value('TEXT_NODE', 402)
    WIDGET = Value('WIDGET', 403)


class DataType(Constant):
    HTML = Value('HTML', 501)
    HTML_TREE = Value('HTML_TREE', 502)
    HTML_UPDATE = Value('HTML_UPDATE', 503)


class Operation(Constant):
    SET = Value('SET', 601)
    RESET = Value('RESET', 602)
    ADD = Value('ADD', 603)
    CLEAR = Value('CLEAR', 604)
    INSERT = Value('INSERT', 605)
    REMOVE = Value('REMOVE', 606)


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
