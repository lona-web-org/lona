from lona import LonaView


class NonInteractiveErrorView(LonaView):
    def handle_request(self, request):
        return str(1 / 0)
