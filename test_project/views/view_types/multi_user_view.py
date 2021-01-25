from datetime import datetime

from lona.html import Strong, Span, Div, H1
from lona.decorators import multi_user


@multi_user
def handle_request(request):
    span = Span()

    html = Div(
        H1('Multi User View'),
        Div(
            Strong('View started: '),
            Span(str(datetime.now())),
        ),
        Div(
            Strong('Now: '),
            span,
        )
    )

    while True:
        span.set_text(str(datetime.now()))
        request.client.show(html)
        request.view.sleep(1)
