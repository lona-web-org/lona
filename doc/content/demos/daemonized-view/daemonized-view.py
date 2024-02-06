import random

from lona.html import Button, HTML, H1
from lona import LonaView, LonaApp

from lona_chartjs import Chart

app = LonaApp(__file__)

app.add_static_file('lona/style.css', """
    body{
        font-family: sans-serif;
    }
""")


@app.route('/')
class DaemonView(LonaView):
    def handle_request(self, request):

        # setup chart and HTML
        chart = Chart({
            'type': 'line',
            'data': {
                'labels': [str(i) for i in range(1, 11)],
                'datasets': [
                    {
                        'label': 'Random Points',
                        'data': [],
                        'backgroundColor': 'red',
                        'borderColor': 'red',
                    },
                ],
            },
            'options': {
                'responsive': False,
            },
        })

        points = chart.data['data']['datasets'][0]['data']

        html = HTML(
            H1('Daemonized View'),
            Button('Add Data Point', _id='add-data-point'),
            chart,
        )

        # tell Lona to not kill the view when the page gets refreshed
        self.is_daemon = True

        while True:
            self.show(html)

            input_event = self.await_click()

            # add a random data point
            if input_event.node_has_id('add-data-point'):
                points.append(random.randint(0, 10))

                if len(points) > 10:
                    points.pop(0)


if __name__ == '__main__':
    app.run(port=8080)
