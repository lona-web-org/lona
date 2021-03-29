from lona.html import Div, H1, P, Strong
from lona import LonaView


class HTTPRedirectView(LonaView):
    def handle_request(self, request):
        s = Strong()

        html = Div(
            H1('Redirect'),
            P('You will be HTTP redirected in ', s, ' seconds'),
        )

        for i in [3, 2, 1]:
            s.set_text(str(i))

            request.client.show(html)

            request.view.sleep(1)

        return {
            'http_redirect': '/',
        }
