from lona.view import LonaView


class URLArgsView(LonaView):
    def handle_request(self, requests, a, b, c):
        return """
            <h2>URL Arguments</h2>
            <div>a={}</div>
            <div>b={}</div>
            <div>c={}</div>
        """.format(a, b, c)
