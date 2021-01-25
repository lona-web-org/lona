from lona.html import HTML, Div, H1


def handle_request(request):
    div = Div()

    html = HTML(
        H1('Interactive View'),
        div,
    )

    while True:
        div.clear()

        for i in range(0, 5):
            div.append(Div('Div {}'.format(i+1)))
            request.client.show(html)

            request.view.sleep(0.5)

        for i in range(0, 5):
            div[i].insert(i+1, Div('Div {}.{}'.format(i+1, i+1)))
            request.client.show(html)

            request.view.sleep(0.5)

        for i in range(0, 5):
            div[i].style = {'color': 'red'}
            request.client.show(html)

            request.view.sleep(0.5)

        request.client.show(html)
