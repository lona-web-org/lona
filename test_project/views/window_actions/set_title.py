from lona.html import HTML, Div, H2, A
from lona.view import View


class WindowTitleView(View):
    def handle_request(self, request):
        div = Div()

        html = HTML(
            H2('Set Title'),
            A('Back', href='/'),
            div,
        )

        self.show(html)

        while True:
            for i in range(3):
                title = f'Title {i}'

                div.set_text(f"Using set_title(); Title should be '{title}'")

                self.set_title(title)
                self.show()

                self.sleep(1)

            for i in range(3):
                title = f'Title {i}'

                div.set_text(f"using show; Title should be '{title}'")
                self.show(html, title=title)

                self.sleep(1)
