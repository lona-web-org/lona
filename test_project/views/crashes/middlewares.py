from lona.view import View


class UnreachableView(View):
    def handle_request(self, request):
        return """
            <h2>Error</h2>
            <p>This view should be unreachable and result in a 500 response</p>
        """
