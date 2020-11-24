from pprint import pformat

from lona.html import Div, Pre, H1

from lona.html.forms import (
    CheckboxField,
    PasswordField,
    ColorField,
    TextField,
    DateField,
    WeekField,
    TimeField,
    Select,
    Form,
)


class TestForm(Form):
    checkbox = CheckboxField('Checkbox', default=False)
    textfield = TextField('Text Field', default='Text')
    passwordfield = PasswordField('Password Field', default='secret')
    color = ColorField('Color Field')

    date = DateField('Date Field')
    week = WeekField('Week Field')
    time = TimeField('Time Field')

    select = Select(
        'Select',
        choices=[
            ('Choice 1', True),
            ('Choice 2', False),
            ('Choice 3', False),
        ]
    )

    select_multiple = Select(
        'Select Multiple',
        multiple=True,
        choices=[
            ('Choice 1', True),
            ('Choice 2', False),
            ('Choice 3', False),
        ]
    )


def handle_request(request):
    form = TestForm()
    pre = Pre(
        style={
            'background-color': 'lightgrey',
        },
    )

    html = Div(
        H1('Interactive Form'),
        Div(
            Div(
                form,
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

    while True:
        pre.set_text(pformat(form.get_values()))
        request.client.await_input_event(html=html)
