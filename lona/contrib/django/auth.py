import logging

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.models import Session

logger = logging.getLogger('lona.contrib.django.auth')


def login_required(function=None):
    def decorator(function):
        function.django_login_required = True

        return function

    if function:
        return decorator(function)

    return decorator


def permission_required(permission):
    def decorator(function):
        if not type(permission) == str:
            raise ValueError('permission has to be a string')

        if not hasattr(function, 'django_permissions_required'):
            function.django_permissions_required = set()

        function.django_permissions_required.add(permission)

        return function

    return decorator


def user_passes_test(test_function):
    def decorator(function):
        if not callable(test_function):
            raise ValueError('test has to be callable')

        if not hasattr(function, 'django_auth_tests'):
            function.django_auth_tests = set()

        function.django_auth_tests.add(test_function)

        return function

    return decorator


def deny_access(server, request, view):
    return {
        'status': 403,
        'title': 'Forbidden',
        'text': '<h1>Forbidden</h1><p>Error 403</p>',
    }


class DjangoSessionMiddleware:
    def process_connection(self, data):
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

    def process_request(self, data):
        request = data.request
        user = request.user
        server = data.server
        settings = server.settings
        view = data.view

        # setup deny access callback
        deny_access_callback = settings.get(
            'DJANGO_AUTH_DENY_ACCESS_CALLBACK',
            deny_access,
        )

        if isinstance(deny_access_callback, str):
            logger.debug("loading DJANGO_AUTH_DENY_ACCESS_CALLBACK from '%s'",
                         deny_access_callback)

            deny_access_callback = server.acquire(deny_access_callback)

            settings.DJANGO_AUTH_DENY_ACCESS_CALLBACK = deny_access_callback

        # check permissions
        logger.debug('%s tries to access %s', user, view)

        if hasattr(view, 'django_login_required') and (
           not user.is_active or
           not user.is_authenticated):

            logger.debug('%s is not authenticated. access denied', user)

            return deny_access_callback(server, request, view)

        if(hasattr(view, 'django_permissions_required') and
           not user.is_superuser and
           not user.has_perms(view.django_permissions_required)):

            logger.debug('%s has not the right permissions %s. access denied',
                         user, view.django_permissions_required)

            return deny_access_callback(server, request, view)

        if hasattr(view, 'django_auth_tests') and not user.is_superuser:
            for test in view.django_auth_tests:
                if not test(user):
                    logger.debug('%s failed %s. access denied', user, test)

                    return deny_access_callback(server, request, view)

        logger.debug('%s: access granted to %s', user, view)

        return data
