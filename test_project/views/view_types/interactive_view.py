from lona.html import HTML, Div, H1
from lona import LonaView


class InteractiveView(LonaView):
    def handle_request(self, request):
        widget = HTML()

        html = HTML(
            H1('Interactive View'),
            widget,
        )

        while True:
            widget.clear()

            for i in range(0, 5):
                widget.append(Div('Div {}'.format(i+1)))
                request.client.show(html)

                request.view.sleep(0.5)

            for i in range(0, 5):
                widget[i].insert(i+1, Div('Div {}.{}'.format(i+1, i+1)))
                request.client.show(html)

                request.view.sleep(0.5)

            for i in range(0, 5):
                widget[i].style = {'color': 'red'}
                request.client.show(html)

                request.view.sleep(0.5)

            moving_div = Div('Div 6', style={'color': 'blue'})

            for i in range(0, 5):
                widget[i].append(moving_div)
                request.client.show(html)

                request.view.sleep(0.5)

            request.client.show(html)
