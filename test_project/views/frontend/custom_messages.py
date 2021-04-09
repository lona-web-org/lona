from datetime import datetime
from time import sleep

from lona.html import HTML, H1
from lona.view import LonaView
from lona.json import dumps


class CustomMessagesView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H1('Messages'),
        )

        request.client.show(html)

        while True:
            private_message = dumps({
                'notification': {
                    'message': '{}: {}'.format(
                        str(datetime.now()),
                        'This is a message',
                    ),
                    'timeout': 2000,
                },
            })

            broadcast_message = dumps({
                'notification': {
                    'message': '{}: {}'.format(
                        str(datetime.now()),
                        'This is a broadcast message',
                    ),
                    'timeout': 2000,
                },
            })

            request.client.send_str(private_message)
            request.client.send_str(broadcast_message, broadcast=True)

            sleep(1)
