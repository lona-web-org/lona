from lona_picocss.html import (
    NumberInput,
    TextInput,
    Switch,
    Label,
    HTML,
    Grid,
    Div,
    H1,
    Br,
)
from lona_picocss import install_picocss

from lona.static_files import Script
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


class RotatingContainer(Div):

    # this tells the frontend the name of the widget to use
    WIDGET = 'RotatingContainer'

    # this tells the frontend that this file has to be loaded
    # before the node can be rendered
    STATIC_FILES = [
        Script(
            name='rotating-container',
            path='rotating-container.js',
        ),
    ]

    STYLE = {
        'display': 'inline-block',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # setting up widget data
        # will be available as `this.data` in the widget
        self.widget_data = {
            'animation_running': True,
            'animation_speed': 2,
        }

    def set_animation_running(self, running):
        self.widget_data['animation_running'] = running

    def set_animation_speed(self, speed):
        self.widget_data['animation_speed'] = speed


@app.route('/')
class Index(View):

    # input event handling
    def set_animation_running(self, input_event):
        self.rotating_container.set_animation_running(input_event.node.value)

    def set_animation_speed(self, input_event):
        self.rotating_container.set_animation_speed(input_event.node.value)

    def set_animation_text(self, input_event):
        self.rotating_container.set_text(input_event.node.value)

    # request handling
    def handle_request(self, request):
        initial_text = 'Weeeeee!'
        self.rotating_container = RotatingContainer(initial_text)

        return HTML(
            H1('Rotating Container'),

            Grid(
                Div(
                    self.rotating_container,
                    Br(),
                    Br(),
                    Br(),
                    Br(),
                    Br(),
                ),
                Div(
                    Label(
                        Switch(
                            value=True,
                            handle_change=self.set_animation_running,
                        ),
                        'Animation',
                    ),
                    Label(
                        'Animation Speed',
                        NumberInput(
                            value=2,
                            handle_change=self.set_animation_speed,
                        ),
                    ),
                    Label(
                        'Text',
                        TextInput(
                            value=initial_text,
                            handle_change=self.set_animation_text,
                        ),
                    ),
                )
            ),
        )


if __name__ == '__main__':
    app.run()
