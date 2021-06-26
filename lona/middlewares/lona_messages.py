import logging

from lona.protocol import PROTOCOL, EXIT_CODE, decode_message

logger = logging.getLogger('lona.protocol')


class AnonymousUser:
    def __repr__(self):
        return '<AnonymousUser()>'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)


class LonaMessageMiddleware:
    def handle_connection(self, data):
        if data.connection.user is None:
            data.connection.user = AnonymousUser()

        return data

    def handle_websocket_message(self, data):
        if not data.message.startswith(PROTOCOL.MESSAGE_PREFIX.value):
            return data

        exit_code, window_id, view_runtime_id, method, payload = \
            decode_message(data.message)

        if exit_code != EXIT_CODE.SUCCESS:
            logger.error('invalid lona message received: %s', data.message)

            return data

        data.server.view_runtime_controller.handle_lona_message(
            connection=data.connection,
            window_id=window_id,
            view_runtime_id=view_runtime_id,
            method=method,
            payload=payload,
        )
