from lona.html import Div, H2, P, Strong
from lona.view import LonaView


class RedirectView(LonaView):
    def handle_request(self, request):
        s = Strong()

        html = Div(
            H2('Redirect'),
            P('You will be redirected in ', s, ' seconds'),
        )

        for i in [3, 2, 1]:
            s.set_text(str(i))

            request.client.show(html)

            request.view.sleep(1)

        return {
            'redirect': '/',
        }
