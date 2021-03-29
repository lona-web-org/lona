from lona import LonaView


class NonInteractiveView(LonaView):
    def handle_request(self, request):
        return """
            <h1>Non Interactive View</h1>
        """
