import logging

from lona.protocol import (
    decode_message,
    encode_pong,
    EXIT_CODE,
    PROTOCOL,
    METHOD,
)

logger = logging.getLogger('lona.protocol')


class LonaMessageMiddleware:
    def handle_websocket_message(self, data):
        if not data.message.startswith(PROTOCOL.MESSAGE_PREFIX.value):
            return data

        exit_code, window_id, view_runtime_id, method, payload = \
            decode_message(data.message)

        if exit_code != EXIT_CODE.SUCCESS:
            logger.error('invalid lona message received: %s', data.message)

            return data

        if method == METHOD.PING:
            data.connection.send_str(encode_pong(), wait=False)

            return

        data.server._view_runtime_controller.handle_lona_message(
            connection=data.connection,
            window_id=window_id,
            view_runtime_id=view_runtime_id,
            method=method,
            payload=payload,
        )
