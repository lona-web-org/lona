class ExitCode:
    SUCCESS = 0
    INVALID_MESSAGE = 1
    INVALID_METHOD = 2


class Method:
    VIEW = 101
    INPUT_EVENT = 102
    REDIRECT = 201
    HTTP_REDIRECT = 202
    DATA = 203
    VIEW_START = 204
    VIEW_STOP = 205


class InputEventType:
    CLICK = 301
    CHANGE = 302
    SUBMIT = 303
    CUSTOM = 304


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


def encode_data(window_id, url, title, html, widget_data,
                patch_input_events=True):

    return [window_id, Method.DATA, url, title, html, widget_data,
            patch_input_events]


def encode_view_start(window_id, url):
    return [window_id, Method.VIEW_START, url]


def encode_view_stop(window_id, url):
    return [window_id, Method.VIEW_STOP, url]
