from lona.html import Strong, Button, Div, CLICK, HTML, H1
from lona import LonaView, LonaApp

from lona_chartjs import Chart

app = LonaApp(__file__)

app.add_static_file('lona/style.css', """
    body{
        font-family: sans-serif;
    }
""")


@app.route('/')
class ChartjsClickAnalyzerView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H1('Chart.js Click Analyzer'),

            Div(
                _id='click',
                nodes=[
                    Div('Click the click area'),
                    Div(Strong(_id='click-counter'), ' clicks to go'),
                    Div(
                        _id='click-area',
                        _style={
                            'width': '500px',
                            'height': '300px',
                            'background-color': 'lightgrey',
                        },
                        events=[CLICK],
                    )
                ],
            ),

            Div(_id='chart'),
        )

        click_div = html.query_selector('#click')
        click_counter = html.query_selector('#click-counter')
        click_area = html.query_selector('#click-area')
        chart_div = html.query_selector('#chart')

        while True:

            # show click area
            click_div.show()
            chart_div.hide()

            # record clicks
            x_positions = []
            y_positions = []

            for i in range(10, 0, -1):
                click_counter.set_text(str(i))

                self.show(html)

                input_event = self.await_click(click_area)

                x_positions.append(input_event.data['x'])
                y_positions.append(input_event.data['y'])

            # render chart
            chart = Chart({
                'type': 'line',
                'data': {
                    'labels': [str(i) for i in range(1, 11)],
                    'datasets': [
                        {
                            'label': 'X Position',
                            'data': x_positions,
                            'backgroundColor': 'red',
                            'borderColor': 'red',
                        },
                        {
                            'label': 'Y Position',
                            'data': y_positions,
                            'backgroundColor': 'blue',
                            'borderColor': 'blue',
                        },
                    ]
                },
                'options': {
                    'responsive': False,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                        }
                    }
                }
            })

            chart.width = '500px'
            chart.height = '300px'

            chart_div.nodes.clear()
            chart_div.nodes.append(Button('Reset'))
            chart_div.nodes.append(chart)

            # show chart
            click_div.hide()
            chart_div.show()

            self.show(html)

            self.await_click()


app.run()
