import threading
import datetime
import time

from lona_picocss.html import Strong, Span, HTML, H1, Br
from lona_picocss import install_picocss

from lona import Channel, View, App

app = App(__file__)

install_picocss(app)

app.settings.PICOCSS_BRAND = 'Clock'
app.settings.PICOCSS_TITLE = 'Clock'


@app.middleware
class ClockMiddleware:
    async def on_startup(self, middleware_data):
        self.people_watching = 0

        # subscribe to clock channels
        self.clock_ticking_channel = Channel('clock.tick')
        self.channel = Channel('clock.*', self.handle_clock_messages)

        # start clock ticking thread
        self.thread = threading.Thread(target=self.tick, daemon=True)

        self.thread.start()

    def handle_clock_messages(self, message):

        # ignore self sent messages
        if message.topic == 'clock.tick':
            return

        # handle joining and leaving of users
        elif message.topic == 'clock.join':
            self.people_watching += 1

        elif message.topic == 'clock.leave':
            self.people_watching -= 1

        self.send_tick()

    def send_tick(self):
        self.clock_ticking_channel.send({
            'time': datetime.datetime.now().strftime('%X'),
            'people_watching': self.people_watching,
        })

    def tick(self):
        while True:
            self.send_tick()

            time.sleep(1)


@app.route('/')
class ClockView(View):
    def handle_request(self, request):

        # setup html
        self.current_time = Span()
        self.people_watching = Span()

        self.html = HTML(
            H1('Clock Demo'),
            Strong('Current time: '),
            self.current_time,
            Br(),
            Strong('People watching:'),
            self.people_watching,
        )

        # subscribe to clock ticking channel
        self.subscribe('clock.tick', self.handle_clock_tick)

        # notify the middleware that we joined
        Channel('clock.join').send()

        return self.html

    def handle_clock_tick(self, message):
        with self.html.lock:
            self.current_time.set_text(message.data['time'])
            self.people_watching.set_text(message.data['people_watching'])

    def on_cleanup(self):

        # notify the middleware that we left
        Channel('clock.leave').send()


app.run()
