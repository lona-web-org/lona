from lona.sessions import AnonymousUser


def lona_session_middleware(server, request, view):
    if not hasattr(request.connection, 'user'):
        request.connection.user = AnonymousUser()
