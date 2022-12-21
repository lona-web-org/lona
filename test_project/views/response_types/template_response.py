from lona.view import View


class TemplateResponseView(View):
    def handle_request(self, request):
        return {
            'template': 'template_response.html',
            'test_variable': 'foo',
        }
