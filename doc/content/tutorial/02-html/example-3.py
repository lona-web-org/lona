from datetime import datetime

from lona_picocss import install_picocss

from lona.html import Strong, Span, HTML, Div, H2, H1, P
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_request(self, request):
        colors = [
            'Tomato',
            'Orange',
            'DodgerBlue',
            'MediumSeaGreen',
            'Gray',
            'SlateBlue',
            'Violet',
            'LightGray',
        ]

        current_color = 0

        # setup the HTML
        timestamp = Strong(str(datetime.now()))
        previous_timestamps = Div()

        html = HTML(
            H1('Clock'),
            P(
                Span('The current time is: '),
                timestamp,
            ),

            H2('Previous Timestamps'),
            previous_timestamps,
        )

        # main loop
        while True:

            # pick a color
            current_color = current_color % len(colors)

            # move the last timestamp to the log
            previous_timestamps.append(
                Div(
                    timestamp.get_text(),
                    style={
                        'color': colors[current_color],
                    },
                ),
            )

            # shorten the previous timestamps if needed
            if len(previous_timestamps) > 5:
                previous_timestamps.nodes[0].remove()

            # set the current time
            timestamp.set_text(datetime.now())
            timestamp.style['color'] = colors[current_color]

            # show html
            self.show(html)

            self.sleep(1)
            current_color += 1


if __name__ == '__main__':
    app.run()
