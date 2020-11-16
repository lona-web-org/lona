def handle_request(request):
    template = """
        <h1>Non-Node Events</h1>
        <div>{}</div>
        <button id="red-button" class="lona-clickable" style="color: white; background-color: red;">Red Button</button>
        <button id="green-button" class="lona-clickable" style="color: white; background-color: green;">Green Button</button>

    """  # NOQA

    message = 'No button pressed'

    while True:
        html = template.format(message)

        input_event = request.client.await_input_event(html)

        if input_event.node_has_id('red-button'):
            message = 'Red Button clicked'

        elif input_event.node_has_id('green-button'):
            message = 'Green Button clicked'

        else:
            message = 'Error: unknown event issuer'
