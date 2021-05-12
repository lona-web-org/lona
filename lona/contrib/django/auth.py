import logging

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.models import Session

logger = logging.getLogger('lona.contrib.django.auth')


class DjangoSessionMiddleware:
    def handle_connection(self, data):
        # find user
        logger.debug('searching for django user')

        if isinstance(data.connection, User):
            return data

        session_key = data.connection.http_request.cookies.get('sessionid', '')
        user = AnonymousUser()

        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)
                uid = session.get_decoded().get('_auth_user_id')

                try:
                    user = User.objects.get(pk=uid)

                except User.DoesNotExist:
                    pass

            except Session.DoesNotExist:
                pass

        logger.debug('user set to %s', user)

        data.connection.user = user

        return data
