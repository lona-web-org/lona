from lona.view import LonaView


class URLArgsView(LonaView):
    def handle_request(self, request):
        return """
            <h2>URL Arguments</h2>
            <div>a={}</div>
            <div>b={}</div>
            <div>c={}</div>
        """.format(
            request.match_info['a'],
            request.match_info['b'],
            request.match_info['c'],
        )
