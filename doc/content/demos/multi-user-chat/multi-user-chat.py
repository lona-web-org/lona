from lona.html import (
    TextInput,
    TextArea,
    Button,
    Table,
    Span,
    HTML,
    Div,
    Ul,
    Tr,
    Td,
    Li,
    H1,
    P,
    A,
)
from lona import LonaView, LonaApp

app = LonaApp(__file__)


@app.route('/')
class ChooseRoom(LonaView):
    def handle_request(self, request):
        # find rooms
        rooms = set()

        with self.server.state.lock:
            if 'rooms' in self.server.state:
                rooms = set(self.server.state['rooms'].keys())

        # setup html
        html = HTML(
            H1('Choose A Chat Room'),

            Ul(
                Li(A(room, href=f'/{room}')) for room in rooms
            ),

            TextInput(
                placeholder='Name',
                _id='new-room-name',
                bubble_up=True,
            ),
            Button('Create', _id='create-new-room'),
        )

        # choose a room
        while True:
            input_event = self.await_input_event(html=html)

            # button
            if input_event.node_has_id('new-room-name'):
                new_room = input_event.node.value

                if new_room in rooms:
                    html.query_selector('#create-new-room').disabled = True

                else:
                    html.query_selector('#create-new-room').disabled = False

            # textinput
            if input_event.node_has_id('create-new-room'):
                new_room = html.query_selector('#new-room-name').value

                return {
                    'redirect': f'/{new_room}',
                }


@app.route('/<room>(/)?')
class Chat(LonaView):

    # messages ################################################################
    def update_messages(self):
        if not hasattr(self, 'messages'):
            return

        with self.room.lock:
            for message_data in self.room['messages'][len(self.messages):]:
                message = Span(message_data['message'])

                if message_data['type'] == 'action':
                    message.style['font-weight'] = 'bold'

                self.messages.append(
                    Div(Span(f'{message_data["issuer"]}: '), message),
                )

    def send_message(self, message, message_type):
        message_data = {
            'room': self.room_name,
            'issuer': self.name,
            'message': message,
            'type': message_type,
        }

        self.room['messages'].append(message_data)

        self.fire_view_event('message', message_data)

    def on_view_event(self, view_event):
        # message is for another room
        if view_event.data['room'] != self.room_name:
            return

        self.update_messages()

    def on_cleanup(self):
        self.room['user'].remove(self.name)

        self.send_message(
            f'{self.name} left',
            message_type='action',
        )

    # gui #####################################################################
    def handle_input_event(self, input_event):
        if not input_event.node_has_id('send'):
            return input_event

        if not self.text_area.value:
            return

        self.send_message(self.text_area.value, message_type='chat')
        self.text_area.value = ''

    def choose_name(self):
        name = TextInput(placeholder='Name')
        message = P(_style='color: red')

        html = HTML(
            H1(self.room_name),
            P('Pick a name'),
            message,
            name,
            Button('Join'),
        )

        while True:
            self.await_click(html=html)

            if not name.value:
                continue

            # check if name is already taken for this room
            with self.server.state.lock:
                if name.value not in self.room['user']:
                    self.room['user'].append(name.value)

                    return name.value

                message.set_text(f'{name.value} already taken')

    def handle_request(self, request):
        self.room_name = request.match_info.get('room')

        # setup room
        with self.server.state.lock:
            if 'rooms' not in self.server.state:
                self.server.state['rooms'] = {}

            if self.room_name not in self.server.state['rooms']:
                self.server.state['rooms'][self.room_name] = {
                    'messages': [],
                    'user': [],
                }

            self.room = self.server.state['rooms'][self.room_name]

        # choose name
        self.name = self.choose_name()

        # setup html
        with self.server.state.lock:
            self.messages = Div()
            self.text_area = TextArea(rows=5)

            self.html = HTML(
                H1(self.room_name),
                self.messages,

                Table(
                    Tr(
                        Td(
                            f'{self.name}: ',
                            _style={'vertical-align': 'top'},
                        ),
                        Td(self.text_area),
                        Td(
                            Button('Send', _id='send'),
                            _style={'vertical-align': 'top'},
                        ),
                    ),
                    _style={
                        'border': 'none',
                        'margin-top': '2em',
                    },
                ),
            )

            self.update_messages()

        self.send_message('Joined', message_type='action')

        return self.html


app.run()
