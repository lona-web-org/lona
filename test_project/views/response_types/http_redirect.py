from lona.html import Strong, Div, P, H2
from lona.view import LonaView


class HTTPRedirectView(LonaView):
    def handle_request(self, request):
        s = Strong()

        html = Div(
            H2('Redirect'),
            P('You will be HTTP redirected in ', s, ' seconds'),
        )

        for i in [3, 2, 1]:
            s.set_text(str(i))

            self.show(html)

            self.sleep(1)

        return {
            'http_redirect': '/',
        }
