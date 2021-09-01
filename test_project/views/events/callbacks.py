from lona.html import HTML, H2, Div, Button
from lona import LonaView


class InputEventCallbackView(LonaView):
    def button_1(self, input_event):
        self.html.query_selector('div').set_text('Button 1 was clicked')

    def button_2(self, input_event):
        self.html.query_selector('div').set_text('Button 2 was clicked')

    def handle_request(self, request):
        self.html = HTML(
            H2('Input Event Callbacks'),
            Div(),
            Button('Button 1', _id='button-1'),
            Button('Button 2', _id='button-2'),
        )

        self.html.query_selector('#button-1').handle_click = self.button_1
        self.html.query_selector('#button-2').handle_click = self.button_2

        return self.html
