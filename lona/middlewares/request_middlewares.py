class AnonymousUser:
    def __repr__(self):
        return '<AnonymousUser()>'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)


def lona_session_middleware(server, request, view):
    if not hasattr(request.connection, 'user'):
        request.connection.user = AnonymousUser()
