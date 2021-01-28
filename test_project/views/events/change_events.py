from lona.html import TextInputNode, CheckboxNode, Div, H1, Pre
from pprint import pformat


def handle_request(request):
    pre = Pre(
        'nothing changed',
        style={
            'background-color': 'lightgrey',
        }
    )

    html = Div(
        H1('Change Events'),
        Div(
            Div(
                Div(CheckboxNode(changeable=True)),
                Div(TextInputNode(changeable=True, value='Change me')),
                style={
                    'float': 'left',
                    'width': '50%',
                },
            ),
            Div(
                pre,
                style={
                    'float': 'left',
                    'width': '50%',
                },
            ),
        ),
    )

    request.client.show(html)

    while True:
        input_event = request.client.await_change(html=html)

        pre.set_text(
            'changed node: {}\nvalue: {}'.format(
                input_event.node._id,
                pformat(input_event.data),
            )
        )
