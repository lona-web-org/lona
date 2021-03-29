class LonaView:
    def handle_user_enter(self, user):
        return True

    def handle_request(self, *args, **kwargs):
        return ''

    def handle_input_event_root(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        return input_event


class FrontendView(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.FRONTEND_TEMPLATE,
            'request': request,
        }


class Error403View(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.ERROR_403_TEMPLATE,
            'request': request,
        }


class Error404View(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.ERROR_404_TEMPLATE,
            'request': request,
        }


class Error500View(LonaView):
    def handle_request(self, request, exception):
        return {
            'template': request.server.settings.ERROR_500_TEMPLATE,
            'request': request,
            'exception': exception,
        }
