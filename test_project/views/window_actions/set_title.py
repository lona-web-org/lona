from lona.html import HTML, Div, H1, A


def handle_request(request):
    div = Div()

    html = HTML(
        H1('Set Title'),
        A('Back', href='/'),
        div,
    )

    request.client.show(html)

    while True:
        for i in range(3):
            title = 'Title {}'.format(i)

            div.set_text(
                "Using set_title(); Title should be '{}'".format(title))

            request.client.set_title(title)
            request.client.show()

            request.view.sleep(1)

        for i in range(3):
            title = 'Title {}'.format(i)

            div.set_text("using show; Title should be '{}'".format(title))
            request.client.show(html, title=title)

            request.view.sleep(1)
