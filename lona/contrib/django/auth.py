import logging

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.models import Session

from lona.errors import ForbiddenError

logger = logging.getLogger('lona.contrib.django.auth')


class DjangoSessionMiddleware:
    def handle_connection(self, data):
        # find user
        logger.debug('searching for django user')

        if isinstance(data.connection.user, User):
            return data

        session_key = data.http_request.cookies.get('sessionid', '')

        if data.server.settings.get('DJANGO_AUTH_USE_LONA_ANONYMOUS_USER',
                                    False):

            user = data.connection.user

        else:
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

    def handle_request(self, data):
        request = data.request

        if request.route.interactive and not request.connection.interactive:
            return data

        view_class = data.server.get_view_class(route=request.route)

        # logging required
        DJANGO_AUTH_LOGIN_REQUIRED = getattr(
            view_class,
            'DJANGO_AUTH_LOGIN_REQUIRED',
            False,
        )

        if DJANGO_AUTH_LOGIN_REQUIRED and not request.user.is_authenticated:
            raise ForbiddenError

        # staff required
        DJANGO_AUTH_STAFF_REQUIRED = getattr(
            view_class,
            'DJANGO_AUTH_STAFF_REQUIRED',
            False,
        )

        if DJANGO_AUTH_STAFF_REQUIRED and not request.user.is_staff:
            raise ForbiddenError

        # staff overrides
        DJANGO_AUTH_STAFF_PERMISSION_OVERRIDE = getattr(
            view_class,
            'DJANGO_AUTH_STAFF_PERMISSION_OVERRIDE',
            True,
        )

        if DJANGO_AUTH_STAFF_PERMISSION_OVERRIDE and request.user.is_staff:
            return data

        # permissions required
        DJANGO_AUTH_PERMISSIONS_REQUIRED = getattr(
            view_class,
            'DJANGO_AUTH_PERMISSIONS_REQUIRED',
            [],
        )

        if DJANGO_AUTH_PERMISSIONS_REQUIRED:
            groups = request.user.permissions.filter(
                name__in=DJANGO_AUTH_PERMISSIONS_REQUIRED,
            ).distinct(
            ).values_list(
                'name',
                flat=True,
            )

            if len(groups) < len(set(DJANGO_AUTH_PERMISSIONS_REQUIRED)):
                raise ForbiddenError

        # groups required
        DJANGO_AUTH_GROUPS_REQUIRED = getattr(
            view_class,
            'DJANGO_AUTH_GROUPS_REQUIRED',
            [],
        )

        if DJANGO_AUTH_GROUPS_REQUIRED:
            groups = request.user.groups.filter(
                name__in=DJANGO_AUTH_GROUPS_REQUIRED,
            ).distinct(
            ).values_list(
                'name',
                flat=True,
            )

            if len(groups) < len(set(DJANGO_AUTH_GROUPS_REQUIRED)):
                raise ForbiddenError

        return data
