from datetime import datetime
from uuid import uuid1
from time import time
import re

from lona_picocss.html import (
    InlineButton,
    ScrollerDiv,
    TextInput,
    TextArea,
    Strong,
    THead,
    TBody,
    Table,
    Span,
    HTML,
    Div,
    Tr,
    Th,
    Td,
    H1,
    Br,
    P,
    A,
)
from lona_picocss import install_picocss

from lona import RedirectResponse, Channel, View, App

NAME = re.compile(r'^([a-zA-Z0-9-_]{1,})$')
MESSAGE_BACK_LOG = 10

app = App(__file__)

install_picocss(app)

app.settings.PICOCSS_BRAND = 'Multi-User Chat'
app.settings.PICOCSS_TITLE = 'Multi-User Chat'

app.settings.INITIAL_SERVER_STATE = {
    'user': {
        # session_key: user_name
    },
    'rooms': {
        # name: {
        #   user: [user_name, ]
        #   log: [
        #       [uuid, unix_timestamp, type, user_name, text, ]
        #   ]
        # }
    },
}


@app.route('/<room>(/)', name='room')
class ChatView(View):
    def show_message(self, message, index=None):
        message_id, unix_timestamp, type, user_name, message = message

        span = Span(style='margin-left: 0.5em')

        line = Div(
            Div(
                Strong(user_name),
                Span(
                    str(datetime.fromtimestamp(unix_timestamp)),
                    style={
                        'color': 'gray',
                        'font-size': '75%',
                        'margin-left': '0.5em',
                    },
                ),
            ),
            span,
            data_message_id=message_id,
        )

        if type == 'message':
            span.set_text(message)

        else:
            span.set_text(f'*{message}*')

            if type == 'join':
                span.style['color'] = 'lime'

            elif type == 'leave':
                span.style['color'] = 'red'

        with self.html.lock:
            if self.messages.query_selector(f'[data-message-id={message_id}]'):
                return

            if index is None:
                self.messages.append(line)

            else:
                self.messages.insert(index, line)

    def send_message(self, type, text):

        # create message
        message = [
            uuid1().hex,
            time(),
            type,
            self.user_name,
            text,
        ]

        # add message to data
        self.room_state['log'].append(message)

        # send message to all clients
        self.channel.send({
            'message': message,
        })

        # trim messages
        while len(self.room_state['log']) > MESSAGE_BACK_LOG:
            self.room_state['log'].pop(0)

    def handle_send_button_click(self, input_event):
        message = self.message_text_area.value.strip()
        self.message_text_area.value = ''

        # nothing to send
        if not message:
            return

        self.send_message('message', message)

    def handle_request(self, request):
        self.room_name = request.match_info['room']
        self.session_key = request.user.session_key
        self.user_name = self.server.state['user'].get(self.session_key, '')
        self.joined = False

        # redirect to lobby if the user has no user name set
        if not self.user_name:
            return RedirectResponse(self.server.reverse('lobby'))

        # check if room exists
        if self.room_name not in self.server.state['rooms']:
            return HTML(
                H1('Room not found'),
                P(f'No room named "{self.room_name}" found'),
            )

        # setup html
        self.room_state = self.server.state['rooms'][self.room_name]

        self.messages = ScrollerDiv(lines=MESSAGE_BACK_LOG, height='50vh')
        self.message_text_area = TextArea(placeholder='Say something nice')

        self.send_button = InlineButton(
            'Send',
            handle_click=self.handle_send_button_click,
        )

        self.html = HTML(
            H1(f'{self.room_name}'),
            self.messages,
            self.message_text_area,
            self.send_button,
        )

        # subscribe to channel
        self.channel = self.subscribe(
            f'chat.room.{self.room_name}',
            lambda message: self.show_message(message.data['message']),
        )

        self.room_state['user'].append(self.user_name)
        self.send_message('join', 'Joined')

        # load history
        for index, message in enumerate(self.room_state['log'].copy()):
            self.show_message(message, index=index)

        self.joined = True

        return self.html

    def on_cleanup(self) -> None:
        if not self.joined:
            return

        self.room_state['user'].remove(self.user_name)
        self.send_message('leave', 'Left')


@app.route('/', name='lobby')
class LobbyView(View):

    # alerts
    def show_error_alert(self, *message):
        with self.html.lock:
            self.alerts.style['color'] = 'red'
            self.alerts.nodes = list(message)

    def show_success_alert(self, *message):
        with self.html.lock:
            self.alerts.style['color'] = 'lime'
            self.alerts.nodes = list(message)

    # user name
    def set_user_name(self, input_event):
        name = self.user_name.value

        if not NAME.match(name):
            self.show_error_alert(f'"{name}" is no valid name')

            return

        if name in self.server.state['user']:
            self.show_error_alert(f'"{name}" is already taken')

            return

        self.server.state['user'][self.session_key] = name

        return RedirectResponse('.')

    # rooms
    def list_rooms(self, *args, **kwargs):
        with self.html.lock:
            self.room_table[-1].clear()

            for name in self.server.state['rooms'].keys():
                user_count = len(self.server.state['rooms'][name]['user'])

                self.room_table[-1].append(
                    Tr(
                        Td(
                            A(
                                name,
                                href=self.server.reverse('room', room=name),
                            ),
                        ),
                        Td(str(user_count)),
                    ),
                )

    def create_room(self, input_event):
        name = self.room_name.value

        if not NAME.match(name):
            self.show_error_alert(f'"{name}" is no valid name')

            return

        if name in self.server.state['rooms']:
            self.show_error_alert(f'"{name}" is already taken')

            return

        self.server.state['rooms'][name] = {
            'user': [],
            'log': [],
        }

        self.room_name.value = ''
        self.show_success_alert(f'"{name}" was created')

        Channel('chat.room.open').send()

    # request handling
    def handle_request(self, request):
        self.session_key = request.user.session_key
        self.alerts = P()

        # set name
        if self.session_key not in self.server.state['user']:
            self.user_name = TextInput(placeholder='User Name')

            self.set_user_name_button = InlineButton(
                'Set',
                handle_click=self.set_user_name,
            )

            self.html = HTML(
                H1('Set User Name'),
                self.alerts,
                self.user_name,
                self.set_user_name_button,
            )

            return self.html

        # select / create room
        self.room_name = TextInput(placeholder='Room Name')

        self.create_room_button = InlineButton(
            'Create Room',
            handle_click=self.create_room,
        )

        self.room_table = Table(
            THead(
                Tr(
                    Th('Room Name'),
                    Th('User Chatting'),
                ),
            ),
            TBody(),
        )

        self.html = HTML(
            H1('Chat Rooms'),

            self.alerts,
            self.room_name,
            self.create_room_button,

            Br(),
            Br(),

            self.room_table,
        )

        self.list_rooms()

        self.channel = self.subscribe(
            'chat.room.*',
            self.list_rooms,
        )

        return self.html


if __name__ == '__main__':
    app.run()
