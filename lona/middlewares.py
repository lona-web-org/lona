import json

from lona.protocol import EXIT_CODE, decode_message


class AnonymousUser:
    # TODO: add cookie support to make anonymous sessions possible

    def __repr__(self):
        return '<AnonymousUser()>'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)


class LonaMessageMiddleware:
    def process_connection(self, data):
        if data.connection.user is None:
            data.connection.user = AnonymousUser()

        return data

    def process_websocket_message(self, data):
        try:
            data.json_data = json.loads(data.message)

        except ValueError:
            data.json_data = None

        if not data.json_data:
            return data

        exit_code, window_id, method, url, payload = decode_message(
            data.json_data,
        )

        if exit_code != EXIT_CODE.SUCCESS:
            return data

        data.server.view_runtime_controller.handle_lona_message(
            connection=data.connection,
            window_id=window_id,
            method=method,
            url=url,
            payload=payload,
        )
