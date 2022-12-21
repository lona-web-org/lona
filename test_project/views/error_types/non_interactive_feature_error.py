from lona.view import View


class NonInteractiveFeatureErrorView(View):
    def handle_request(self, request):
        return {
            'json': {'foo': 'bar'},
        }
