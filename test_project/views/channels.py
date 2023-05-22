from datetime import datetime

from lona.html import TextInput, TextArea, Button, HTML, Pre, H2, Br
from lona import Channel, View

MESSAGE_BACKLOG = 30


class ChannelsView(View):
    def handle_request(self, request):
        self.receive_channel = None

        if 'id' in request.GET:
            if 'messages' not in self.server.state:
                self.server.state['messages'] = {}

            self.server.state['messages'][request.GET['id']] = []

        # receive
        self.receive_topic = TextInput(
            placeholder='Topic',
            value='*',
            _id='receive-topic',
        )

        self.received_messages = Pre()

        # send
        self.send_topic = TextInput(
            placeholder='Topic',
            value='*',
            _id='send-topic',
        )

        self.send_text_area = TextArea(
            placeholder='Message',
            _id='send-message',
        )

        self.html = HTML(
            # send
            H2('Send'),
            self.send_topic,
            Br(),
            self.send_text_area,
            Br(),
            Button('Send', handle_click=self.send_message),

            # receive
            H2('Receive'),

            self.receive_topic,
            Button('Connect', handle_click=self.connect),
            ' ',
            Button('Clear', handle_click=self.clear),
            Br(),

            self.received_messages,
        )

        self.connect(None)

        return self.html

    def connect(self, input_event):
        if self.receive_channel:
            self.receive_channel.unsubscribe()

        self.receive_channel = self.subscribe(
            topic=self.receive_topic.value,
            handler=self.handle_message,
        )

    def send_message(self, input_event):
        Channel(self.send_topic.value).send({
            'message': self.send_text_area.value,
        })

    def clear(self, input_event):
        self.received_messages.clear()

    def handle_message(self, message):
        if 'id' in self.request.GET:
            self.server.state['messages'][self.request.GET['id']].append(
                message,
            )

        with self.html.lock:
            self.received_messages.insert(
                0,
                f'{datetime.now()}: {message.topic}: {str(message.data)}\n',
            )

            self.received_messages.nodes = \
                self.received_messages.nodes[0:MESSAGE_BACKLOG]

        self.show()
