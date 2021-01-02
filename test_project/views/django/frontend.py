import logging

from lona.views import frontend as _frontend

logger = logging.getLogger('test_project')


def frontend(request):
    logger.info('running frontend as %s', request.user)

    return _frontend(request)
