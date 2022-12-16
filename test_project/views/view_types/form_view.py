from pprint import pformat

from lona.html import TextInput, Submit, Button, HTML, Form, Pre, Div, H2, Br
from lona.view import View


class FormView(View):
    def handle_request(self, request):
        request_data = {
            'GET': request.GET,
            'POST': request.POST,
        }

        message = Div()

        html = HTML(
            H2('Form View'),
            Pre(pformat(request_data)),

            Button('Interactive GET', _id='interactive-get'),
            Button('Interactive POST', _id='interactive-post'),
            Br(),
            Button('Non Interactive GET', _id='non-interactive-get'),
            Button('Non Interactive POST', _id='non-interactive-post'),
        )

        input_event = self.await_click(html=html)

        action = '.'
        method = 'post'

        if (input_event.node_has_id('non-interactive-get') or
                input_event.node_has_id('interactive-get')):

            method = 'get'

        html = HTML(
            H2('Form View'),
            message,
            Form(
                TextInput(name='text'),
                Submit('Submit'),
                method=method,
                action=action,
            ),
        )

        if (input_event.node_has_id('non-interactive-get') or
                input_event.node_has_id('non-interactive-post')):

            message.set_text('View stopped')

            return html

        else:
            message.set_text('View waits for input events')

            self.await_input_event(html=html)
