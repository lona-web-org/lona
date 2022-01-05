from lona.html import TextInput, HTML, Div, H2, Br
from lona.view import LonaView
from lona.events import FOCUS


class FocusEventsView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H2('Focus Events'),
            Div('No text input focused yet'),
            Br(),
            TextInput(_id='1', placeholder='1', events=[FOCUS]),
            TextInput(_id='2', placeholder='2', events=[FOCUS]),
            TextInput(_id='3', placeholder='3', events=[FOCUS]),
            TextInput(_id='4', placeholder='4', events=[FOCUS]),
            TextInput(_id='5', placeholder='5', events=[FOCUS]),
        )

        while True:
            input_event = self.await_focus(html=html)

            html.query_selector('div').set_text(
                f'{list(input_event.node.id_list)[0]} was focused',
            )
