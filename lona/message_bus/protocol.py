import json

from lona.json import dumps


def decode_message(raw_message):
    """
    Decode raw messages.

    Every message has to be an JSON encoded list containing exactly:
        - issuer (string)
        - topic (string)
        - params (any)
    """

    try:
        message = json.loads(raw_message)

    except json.JSONDecodeError:
        return False, None

    if not isinstance(message, list):
        return False, None

    if not len(message) == 3:
        return False, None

    if not isinstance(message[0], str):
        return False, None

    if not isinstance(message[1], str):
        return False, None

    return True, message


def encode_message(issuer, topic, params=None):
    """
    Encode a message into JSON.

    This function takes:
        - issuer (string)
        - topic (string)
        - params (any), (optional)
    """

    if not isinstance(issuer, str):
        raise ValueError('issuer has to be string')

    if not isinstance(issuer, str):
        raise ValueError('topic has to be string')

    return dumps([issuer, topic, params])
