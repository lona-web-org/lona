from lona.html import HTML, Div, H2, A
from lona.view import LonaView


class WindowTitleView(LonaView):
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
                title = 'Title {}'.format(i)

                div.set_text(
                    "Using set_title(); Title should be '{}'".format(title))

                self.set_title(title)
                self.show()

                self.sleep(1)

            for i in range(3):
                title = 'Title {}'.format(i)

                div.set_text("using show; Title should be '{}'".format(title))
                self.show(html, title=title)

                self.sleep(1)
