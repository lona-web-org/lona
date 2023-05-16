import string
import random

from aiohttp.web import Response

from lona.imports import acquire

REDIRECT_BODY = """
<html>
    <head>
        <meta http-equiv="refresh" content="0; url={url}" />
    </head>
    <body>
    </body>
</html>
""".strip()


def generate_random_string(length):
    choices = string.ascii_letters + string.digits
    return ''.join(random.choice(choices) for _ in range(length))


def generate_session_key(connection):
    return generate_random_string(
        connection.server.settings.SESSIONS_KEY_RANDOM_LENGTH)


class AnonymousUser:
    def __init__(self, session_key=''):
        self.session_key = session_key

    def __repr__(self):
        return f'<AnonymousUser({self.session_key})>'

    def __eq__(self, other):
        if not isinstance(other, AnonymousUser):
            return False

        return self.session_key == other.session_key


class LonaSessionMiddleware:
    async def on_startup(self, data):

        # import session key generator
        self.generate_session_key = await data.server.run_function_async(
            acquire,
            data.server.settings.SESSIONS_KEY_GENERATOR,
        )

    def handle_connection(self, data):
        connection = data.connection
        http_request = data.connection.http_request
        settings = data.server.settings
        router = data.server._router

        # user is already set
        # nothing to do
        if connection.user is not None:
            return data

        # sessions are disabled
        if not settings.SESSIONS:
            connection.user = AnonymousUser()

            return data

        # session reuse is disabled
        # generating a new random session
        if not settings.SESSIONS_REUSE:
            connection.user = AnonymousUser(
                session_key=self.generate_session_key(connection),
            )

            return data

        # get session key
        session_key = http_request.cookies.get(settings.SESSIONS_KEY_NAME, '')

        # no previous session found
        # setting a new session key using a redirect
        if not connection.interactive and not session_key:

            # skip cookie setting and redirecting on non-interactive routes
            # without this exception REST APIs don't work as expected
            match, route, _ = router.resolve(http_request.path)

            if match and not route.interactive:
                return data

            # set cookie and redirect so the cookie will take effect
            response = Response(
                status=200,
                content_type='text/html',
                text=REDIRECT_BODY.format(url=http_request.path),
            )

            session_key = self.generate_session_key(connection)

            response.cookies[settings.SESSIONS_KEY_NAME] = session_key

            return response

        # previous session found
        connection.user = AnonymousUser(session_key=session_key)

        return data
