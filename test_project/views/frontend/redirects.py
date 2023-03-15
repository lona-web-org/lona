from lona.html import TextInput, Button, Label, HTML, Div, H2, A
from lona import HttpRedirectResponse, RedirectResponse, View


class RedirectsView(View):
    def handle_url_change(self, input_event):
        self.link.set_href(self.text_input.value)

    def redirect(self, input_event):
        return RedirectResponse(
            self.text_input.value,
        )

    def http_redirect(self, input_event):
        return HttpRedirectResponse(
            self.text_input.value,
        )

    def handle_request(self, request):
        self.link = A(
            'Link',
            href='#',
            id='link',
            ignore=True,
        )

        self.text_input = TextInput(
            placeholder='URL',
            id='url',
            handle_change=self.handle_url_change,
        )

        self.html = HTML(
            H2('Redirects'),
            Div(
                Label(
                    'URL: ',
                    self.text_input,
                ),
                Button(
                    'Redirect',
                    id='redirect',
                    handle_click=self.redirect,
                ),
                Button(
                    'HTTP Redirect',
                    id='http-redirect',
                    handle_click=self.http_redirect,
                ),
            ),
            Div(
                Label(
                    'Link: ',
                    self.link,
                ),
            ),
        )

        return self.html
