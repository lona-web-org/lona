import logging

from lona.default_views import FrontendView as _FrontendView

logger = logging.getLogger('test_project')


class FrontendView(_FrontendView):
    def handle_request(self, request):
        logger.info('running frontend as %s', request.user)

        return self.render_default_template(request)
