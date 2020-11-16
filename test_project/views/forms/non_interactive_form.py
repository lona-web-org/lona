from pprint import pformat

from lona.html import Div, Pre, H1, Hr, Br, A
from lona.html.forms import Form

from lona.html.forms import CheckboxField, TextField


class TestForm(Form):
    checkbox = CheckboxField('Checkbox', default=False)
    textfield = TextField('Text Field', default='Text')


def handle_request(request):
    links = [
        A('Reset', href='/forms/implicit-non-interactive-form/'),
        Br(),
    ]

    if 'form-method' in request.GET:
        form_method = request.GET.pop('form-method')

    else:
        form_method = 'get'

    if form_method == 'get':
        links.append(A('POST Mode', href='./?form-method=post'))

    else:
        links.append(A('GET Mode', href='./?form-method=get'))

    # setup form
    if request.method == 'GET':
        initial = request.GET

    else:
        initial = request.POST

    form = TestForm(initial=initial, method=form_method)

    form.run_checks()

    # setup html
    html = Div(
        H1('Non-Interactive Form'),
        Div(
            *links,
            Hr(),
            form,
            style={
                'float': 'left',
                'width': '50%',
            },
        ),
        Div(
            Pre(
                'request.method: {}'.format(request.method),
                'request.GET: {}'.format(pformat(request.GET)),
                'request.POST: {}'.format(pformat(request.POST)),
                'form values: {}'.format(pformat(form.get_values())),
                style={
                    'background-color': 'lightgrey',
                },
            ),
            style={
                'float': 'left',
                'width': '50%',
            },
        ),
    )

    return html
