from random import randint

from lona.html import HTML, Button, Div, H1
from lona.contrib.chartjs import Chart


def handle_request(request):
    chart_data = {
       'labels': [
           'January',
           'February',
           'March',
           'April',
           'May',
           'June',
           'July',
       ],
       'datasets': [{
           'label': 'My First dataset',
           'backgroundColor': 'rgb(132, 99, 255)',
           'borderColor': 'rgb(132, 99, 255)',
           'data': [0, 10, 5, 2, 20, 30, 45],
       }]
    }

    chart = Chart(
        type='line',
        data=chart_data.copy(),
    )

    chart2 = Chart(
        type='line',
        data=chart_data.copy(),
    )

    html = HTML(
        H1('Chart.js'),
        Button('Update'),
        Div(
            chart,
            style={
                'width': '600px',
            },
        ),
        Div(
            chart2,
            style={
                'width': '600px',
            },
        ),
    )

    while True:
        request.client.await_input_event(html=html)

        chart.data['data']['datasets'][0]['data'].append(randint(0, 100))
        chart.data['data']['datasets'][0]['data'].pop(0)

        chart2.data['data']['datasets'][0]['data'].append(randint(0, 100))
        chart2.data['data']['datasets'][0]['data'].pop(0)
