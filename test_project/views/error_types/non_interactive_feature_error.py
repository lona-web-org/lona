from lona import LonaView


class NonInteractiveFeatureErrorView(LonaView):
    def handle_request(self, request):
        return {
            'json': {'foo': 'bar'},
        }
