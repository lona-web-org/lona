import math

from lona.html import TextInput, HTML, H1
from lona import View, App

from lona_chartjs.html import Chart

app = App(__file__)

app.add_static_file('lona/style.css',"""
#lona {
    font-family: sans-serif;
    color: #333333;
    max-width: 95%;
    margin: 0 auto;
}
""")

colors = {
    'red': 'rgba(255, 99, 132, 1)',
    'blue': 'rgba(54, 162, 235, 1)',
    'yellow': 'rgba(255, 206, 86, 1)',
    'green': 'rgba(75, 192, 192, 1)',
    'purple': 'rgba(153, 102, 255, 1)',
    'orange': 'rgba(255, 159, 64, 1)',
    'grey': 'rgba(201, 203, 207, 1)',
}


def alpha(color, alpha):
    return colors[color].replace('1)', str(alpha) + ')')


CHART_DATA = {
    'type': 'line',
    'data': {
        'labels': [],
        'datasets': [
            {
                'label': 'f₁',
                'data': [],
                'borderWidth': 2,
                'borderColor': colors['blue'],
                'backgroundColor': alpha('blue', 0.2),
            },
            {
                'label': 'f₂',
                'data': [],
                'borderWidth': 2,
                'borderColor': colors['green'],
                'backgroundColor': alpha('green', 0.2),
            },
            {
                'label': 'f₃',
                'data': [],
                'borderWidth': 2,
                'borderColor': colors['orange'],
                'backgroundColor': alpha('orange', 0.2),
            },
        ]
    },
    'options': {
        'animation': False,
        'responsive': False,
        'scales': {
            'y': {
                'beginAtZero': True,
            }
        }
    }
}


@app.route('/')
class MyLonaView(View):
    def handle_request(self, request):
        self.chart = Chart(
            width='600px',
            height='400px',
            data=CHART_DATA,
        )

        self.f1 = TextInput(
            'x*x/30-0.5',
            handle_change=self.handle_text_input_change,
        )

        self.f2 = TextInput(
            'sin(x)',
            handle_change=self.handle_text_input_change,
        )

        self.f3 = TextInput(
            'e**(-x*x)',
            handle_change=self.handle_text_input_change,
        )

        self.x_min = -6.3
        self.x_max = 6.3
        self.point_count = 60

        self.xmin = TextInput(
            self.x_min,
            handle_change=self.handle_text_input_change,
        )

        self.xmax = TextInput(
            self.x_max,
            handle_change=self.handle_text_input_change,
        )

        self.points = TextInput(
            self.point_count,
            handle_change=self.handle_text_input_change,
        )

        html = HTML(
            H1('Function Plotter'),
            'f<sub>1</sub>:', '&nbsp;', self.f1, '&nbsp;&nbsp;&nbsp;',
            'f<sub>2</sub>:', '&nbsp;', self.f2, '&nbsp;&nbsp;&nbsp;',
            'f<sub>3</sub>:', '&nbsp;', self.f3,
            '<br>',
            self.chart,
            'x<sub>min</sub>:', '&nbsp;', self.xmin, '&nbsp;&nbsp;&nbsp;',
            'x<sub>max</sub>:', '&nbsp;', self.xmax, '&nbsp;&nbsp;&nbsp;',
            'points:', '&nbsp;', self.points,
        )

        self.handle_text_input_change(type('', (), {'data': self.f1.value}))

        self.show(html)

    def handle_text_input_change(self, input_event):
        try:
            self.x_min = float(self.xmin.value)
            self.xmin.style = {'color': 'black', 'width' : '4em'}
        except:
            self.xmin.style = {'color': 'red', 'width' : '4em'}
        try:
            self.x_max = float(self.xmax.value)
            self.xmax.style = {'color': 'black', 'width' : '4em'}
        except:
            self.xmax.style = {'color': 'red', 'width' : '4em'}
        try:
            if float(self.points.value) == 0:
                raise RuntimeError
            self.point_count = float(self.points.value)
            self.points.style = {'color': 'black', 'width' : '4em'}
        except:
            self.points.style = {'color': 'red', 'width' : '4em'}
        step = (self.x_max - self.x_min) / self.point_count
        f_list = [self.f1, self.f2, self.f3]
        color_list = ['blue', 'green', 'orange']
        for i in range(len(f_list)):
            x_list = []
            y_list = []
            exception_count = 0
            x = self.x_min
            while x < self.x_max + step / 2:
                x_list.append(round(x, 1))
                y = 0
                try:
                    y = float(eval(f_list[i].value, math.__dict__, {'x': x}))
                except:
                    exception_count += 1
                y_list.append(y)
                x += step
            if exception_count < len(x_list):
                CHART_DATA['data']['labels'] = x_list
                CHART_DATA['data']['datasets'][i]['data'] = y_list
                self.chart.data = CHART_DATA
                f_list[i].style = {'color': color_list[i]}
            else:
                f_list[i].style = {'color': 'red'}


app.add_template('lona/frontend.js', """
    lona_context.add_disconnect_hook(function(lona_context, event) {
        document.querySelector('#lona').innerHTML = `
            Server disconnected <br> Trying to reconnect...
        `;

        setTimeout(function() {
            lona_context.reconnect();

        }, 1000);
    });
""")


app.run()
