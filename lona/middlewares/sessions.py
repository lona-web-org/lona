import logging

logger = logging.getLogger('lona.sessions')


class AnonymousUser:
    def __repr__(self):
        return '<AnonymousUser()>'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)


class LonaSessionMiddleware:
    def handle_connection(self, data):
        if data.connection.user is None:
            data.connection.user = AnonymousUser()

        return data
