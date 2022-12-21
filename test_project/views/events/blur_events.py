from lona.html import TextInput, HTML, Div, H2, Br
from lona.events import BLUR
from lona.view import View


class BlurEventsView(View):
    def handle_request(self, request):
        html = HTML(
            H2('Blur Events'),
            Div('No text input blured yet'),
            Br(),
            TextInput(_id='1', placeholder='1', events=[BLUR]),
            TextInput(_id='2', placeholder='2', events=[BLUR]),
            TextInput(_id='3', placeholder='3', events=[BLUR]),
            TextInput(_id='4', placeholder='4', events=[BLUR]),
            TextInput(_id='5', placeholder='5', events=[BLUR]),
        )

        while True:
            input_event = self.await_blur(html=html)

            html.query_selector('div').set_text(
                f'{list(input_event.node.id_list)[0]} was blured',
            )
