from datetime import datetime

from lona.html import HTML, H2
from lona.view import LonaView
from lona._json import dumps


class CustomMessagesView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H2('Messages'),
        )

        self.show(html)

        while True:
            private_message = dumps({
                'notification': {
                    'message': f'{datetime.now()}: This is a message',
                    'timeout': 2000,
                },
            })

            broadcast_message = dumps({
                'notification': {
                    'message': f'{datetime.now()}: This is a broadcast message',  # NOQA: E501
                    'timeout': 2000,
                },
            })

            self.send_str(private_message)
            self.send_str(broadcast_message, broadcast=True)

            self.sleep(1)
