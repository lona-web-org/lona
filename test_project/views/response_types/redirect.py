from lona.html import Button, HTML, H2, Br, A
from lona.view import LonaView


class RedirectView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H2('Redirect'),
            Button('Absolute URI', _id='redirect-to-absolute-uri'),
            Button('Redirect to root', _id='redirect-to-root'),
            Button('Redirect to this URL', _id='redirect-to-this-url'),

            H2('Links'),
            A(
                '(interactive) /view-types/interactive-view/',
                href='/view-types/interactive-view/',
            ),

            Br(),

            A(
                '(non-interactive) /view-types/interactive-view/',
                href='/view-types/interactive-view/',
                interactive=False,
            ),

            Br(),

            A('www.example.org/foo/bar', href='www.example.org/foo/bar'),
            Br(),

            A(
                'http://www.example.org/foo/bar',
                href='http://www.example.org/foo/bar',
            ),
        )

        self.show(html)

        input_event = self.await_click()

        if input_event.node_has_id('redirect-to-absolute-uri'):
            return {
                'redirect': '/view-types/interactive-view/',
            }

        elif input_event.node_has_id('redirect-to-root'):
            return {
                'redirect': '/',
            }

        elif input_event.node_has_id('redirect-to-this-url'):
            return {
                'redirect': '.',
            }
