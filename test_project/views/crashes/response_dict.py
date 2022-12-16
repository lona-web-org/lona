from lona.view import View


class ResponseDictView(View):
    def handle_request(self, request):
        return {
            'template_string': 'foo',
            'template': 'bar',
        }
