import asyncio

from lona.html import Button, HTML, Div, H2, Br
from lona.view import LonaView


async def short_running_coroutine():
    return 'foo'


async def long_running_coroutine():
    while True:
        print('>> long_running_coroutine()')

        await asyncio.sleep(1)


async def show_html(view):
    view.show("Error: You shouldn't see this!")


class AsyncView(LonaView):
    def handle_request(self, request):
        try:
            html = HTML(
                H2('Async View'),
                Div(),

                Br(),

                Button('Sleep forever', _id='sleep-forever'),

                Button('Await short running coroutine',
                       _id='await-short-running-coroutine'),

                Button('Await long running coroutine',
                       _id='await-long-running-coroutine'),

                Button('Show HTML', _id='show-html'),
                Button('Crash', _id='crash'),
            )

            input_event = self.await_input_event(html=html)

            if input_event.node_has_id('sleep-forever'):
                html[1].set_text('Sleeping forever')

                self.show(html)

                self.sleep(300)

            elif input_event.node_has_id('await-short-running-coroutine'):
                return_value = self.await_sync(
                    short_running_coroutine(),
                )

                html[1].set_text(
                    f'short_running_coroutine() returned {return_value!r}',
                )

                self.show(html)

            elif input_event.node_has_id('await-long-running-coroutine'):
                html[1].set_text('running long_running_coroutine()')

                self.show(html)

                self.await_sync(long_running_coroutine())

            elif input_event.node_has_id('show-html'):
                self.await_sync(show_html(self))

            return html

        finally:
            print('>> async view stopped')

    def handle_input_event_root(self, input_event):
        if input_event.node_has_id('crash'):
            raise ValueError('Success! This should crash!')

        return input_event
