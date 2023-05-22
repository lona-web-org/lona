from lona_picocss.html import InlineButton, TextArea, HTML, Pre, H1
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app)


@app.route('/<name>')
class Index(View):
    def send_message(self, input_event):
        message = self.text_area.value.strip()

        if not message:
            return

        self.channel.send({
            'name': self.name,
            'message': message,
        })

        self.text_area.value = ''

    def handle_message(self, message):
        self.messages.write_line(
            f"{message.data['name']}: {message.data['message']}",
        )

    def handle_request(self, request):
        self.name = request.match_info['name']

        # setup html
        self.messages = Pre(style='height: 10em')
        self.text_area = TextArea(placeholder='Say something nice')

        self.html = HTML(
            H1(f'Chatting as {self.name}'),
            self.messages,
            self.text_area,
            InlineButton(
                'Send',
                handle_click=self.send_message,
            ),
        )

        # subscribe to channel
        self.channel = self.subscribe(
            topic='chat',
            handler=self.handle_message,
        )

        return self.html


app.run()
