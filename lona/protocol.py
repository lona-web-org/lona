class ExitCode:
    SUCCESS = 0
    INVALID_MESSAGE = 1
    INVALID_METHOD = 2


class Method:
    VIEW = 11
    INPUT_EVENT = 12
    REDIRECT = 13
    HTML = 14
    DESKTOP_NOTIFICATION = 15


class InputEventType:
    CLICK = 21
    CHANGE = 22
    SUBMIT = 23
    RESET = 24  # TODO: remove (frontend) forms do reset themself)
    CUSTOM = 25


def decode_message(message):
    """
    returns: (exit_code, method, url, payload)

    """

    if not isinstance(message, list):
        return ExitCode.INVALID_MESSAGE, None, None, None

    # view
    if message[0] == Method.VIEW:
        if not isinstance(message[1], str):
            return ExitCode.INVALID_MESSAGE, None, None, None

        payload = None

        if len(message) > 2:
            payload = message[2]

        return ExitCode.SUCCESS, Method.VIEW, message[1], payload

    # input event
    if message[0] == Method.INPUT_EVENT:
        if not isinstance(message[1], str):
            return ExitCode.INVALID_MESSAGE, None, None, None

        if not (isinstance(message[2], str) or 25 > message[2] > 20):
            return ExitCode.INVALID_MESSAGE, None, None, None

        return ExitCode.SUCCESS, Method.INPUT_EVENT, message[1], message[2:]

    return ExitCode.INVALID_MESSAGE, None, None


def encode_html(url, html, input_events=True):
    if not isinstance(url, str):
        raise TypeError('url has to be string')

    if not isinstance(html, (str, dict)):
        raise TypeError('html has to be string or dict')

    if not isinstance(input_events, bool):
        raise TypeError('input_events has to be bool')

    return [Method.HTML, url, html, input_events]


def encode_redirect(url, interactive=True):
    if not isinstance(url, str):
        raise TypeError('url has to be string')

    if not isinstance(interactive, bool):
        raise TypeError('interactive has to be bool')

    return [Method.REDIRECT, url, interactive]
