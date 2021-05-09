import logging

from lona.view import LonaView

logger = logging.getLogger('lona.views')


class FallbackView(LonaView):
    VIEW_SETTING = ''
    TEMPLATE_SETTING = ''

    def render_default_template(self, request, **extra_contenxt):
        template_setting = request.server.settings.get(self.TEMPLATE_SETTING)

        return {
            'template': template_setting,
            'request': request,
            **extra_contenxt,
        }

    def handle_request(self, request, **extra_contenxt):
        view_setting = request.server.settings.get(self.VIEW_SETTING, '')

        if view_setting:
            try:
                view_class = request.server.view_loader.load(view_setting)

                view = view_class(
                    server=self.server,
                    view_runtime=self.view_runtime,
                )

                return view.handle_request(request, **extra_contenxt)

            except Exception:
                logger.error(
                    "exception raised while running '%s'. running fallback view",  # NOQA
                    view_setting,
                    exc_info=True,
                )

                return self.render_default_template(request, **extra_contenxt)

        return self.render_default_template(request, **extra_contenxt)


class FrontendView(FallbackView):
    VIEW_SETTING = 'FRONTEND_VIEW'
    TEMPLATE_SETTING = 'FRONTEND_TEMPLATE'


class Error403View(FallbackView):
    VIEW_SETTING = 'ERROR_403_VIEW'
    TEMPLATE_SETTING = 'ERROR_403_TEMPLATE'


class Error404View(FallbackView):
    VIEW_SETTING = 'ERROR_404_VIEW'
    TEMPLATE_SETTING = 'ERROR_404_TEMPLATE'


class Error500View(FallbackView):
    VIEW_SETTING = 'ERROR_500_VIEW'
    TEMPLATE_SETTING = 'ERROR_500_TEMPLATE'
