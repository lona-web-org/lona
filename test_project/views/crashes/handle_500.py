from lona import LonaView


class CrashingView(LonaView):
    def handle_request(self, request):
        raise ValueError('This invokes the 500 handler')
