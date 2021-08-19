import random
import string

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
    characters = []
    choices = string.ascii_letters + string.digits

    for i in range(length):
        characters.append(random.choice(choices))

    return ''.join(characters)


def generate_session_key(connection):
    return generate_random_string(
        connection.server.settings.SESSIONS_KEY_RANDOM_LENGTH)


class AnonymousUser:
    def __init__(self, session_key=''):
        self.session_key = session_key

    def __repr__(self):
        return '<AnonymousUser({})>'.format(self.session_key)

    def __eq__(self, other):
        if not isinstance(other, AnonymousUser):
            return False

        return self.session_key == other.session_key


class LonaSessionMiddleware:
    async def on_startup(self, data):
        self.generate_session_key = await data.server.run_function_async(
            acquire,
            data.server.settings.SESSIONS_KEY_GENERATOR,
        )

    def handle_connection(self, data):
        http_request = data.connection.http_request
        settings = data.server.settings
        router = data.server.router

        def get_session_key():
            if settings.SESSIONS_KEY_NAME not in http_request.cookies:
                return ''

            return http_request.cookies[settings.SESSIONS_KEY_NAME]

        if not settings.SESSIONS:
            if data.connection.user is None:
                data.connection.user = AnonymousUser()

            return data

        if(not data.connection.interactive and
           not get_session_key()):

            # skip cookie setting and redirecting on non-interactive routes
            # without this exception REST APIs don't work as expected
            match, route, match_info = router.resolve(http_request.path)

            if match and not route.interactive:
                return data

            # set cookie and redirect so the cookie will take effect
            response = Response(
                status=200,
                content_type='text/html',
                text=REDIRECT_BODY.format(url=http_request.path),
            )

            session_key = self.generate_session_key(data.connection)

            response.cookies[settings.SESSIONS_KEY_NAME] = session_key

            return response

        if data.connection.user is None:
            data.connection.user = AnonymousUser(
                session_key=get_session_key(),
            )

        return data
