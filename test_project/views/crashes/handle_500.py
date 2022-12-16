from lona.view import View


class CrashingView(View):
    def handle_request(self, request):
        raise ValueError('This invokes the 500 handler')
