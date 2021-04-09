from lona.view import LonaView


class FileResponseView(LonaView):
    def handle_request(self, request):
        return {
            'file': __file__,
        }
