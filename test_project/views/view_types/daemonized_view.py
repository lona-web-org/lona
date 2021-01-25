from lona.html import Div, H1, Button


def handle_request(request, name='blank'):
    message = Div('View not started yet')
    log = Div()
    start = Button('Start')
    start_daemonized = Button('Start daemonized')

    html = Div(
        H1('Daemonized View (name={})'.format(name)),
        message,
        log,
        start,
        start_daemonized,
    )

    input_event = request.client.await_input_event(html=html)

    if input_event.node == start_daemonized:
        request.view.daemonize()

        message.set_text('View started daemonized')

    else:
        message.set_text('View started normal')

    for i in range(15):
        log.set_text('Counting ({}/15)'.format(i+1))
        request.client.show(html)

        request.view.sleep(1)

    message.set_text('View stopped')
    request.client.show(html)
