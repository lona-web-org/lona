import logging

from lona.views import FrontendView as _FrontendView

logger = logging.getLogger('test_project')


class FrontendView(_FrontendView):
    def handle_request(self, request):
        logger.info('running frontend as %s', request.user)

        return super().handle_request(request)
