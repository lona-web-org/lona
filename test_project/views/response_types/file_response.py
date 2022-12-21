from lona.view import View


class FileResponseView(View):
    def handle_request(self, request):
        return {
            'file': __file__,
        }
