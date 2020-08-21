import logging
import json

from lona.protocol import ExitCode, decode_message

logger = logging.getLogger('lona.middlewares.websocket_middlewares')


class WebSocketMessage(str):
    def __new__(cls, raw_string):
        obj = super().__new__(cls, raw_string)

        obj.json_data = None

        return obj


def json_middleware(server, connection, raw_message):
    message = WebSocketMessage(raw_message)

    try:
        message.json_data = json.loads(raw_message)

    except ValueError:
        pass

    return message


def lona_message_middleware(server, connection, message):
    if not message.json_data:
        return message

    exit_code, method, url, payload = decode_message(message.json_data)

    # message cannot be parsed and gets passed down
    if exit_code != ExitCode.SUCCESS:
        return message

    server.view_controller.handle_lona_message(
        connection, method, url, payload)
