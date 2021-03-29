from pprint import pformat

from lona.html import HTML, H1, Submit, Form, Div, Pre
from lona.contrib.django.forms import DjangoForm
from lona import LonaView

from django import forms


class TestForm(forms.Form):
    text = forms.CharField(max_length=3, initial='foo')

    select = forms.NullBooleanField(
        widget=forms.Select(
            choices=[
                ('option-a', 'Option A'),
                ('option-b', 'Option B'),
                ('option-c', 'Option C'),
            ]
        )
    )

    select_multiple = forms.NullBooleanField(
        widget=forms.SelectMultiple(
            choices=[
                ('option-a', 'Option A'),
                ('option-b', 'Option B'),
                ('option-c', 'Option C'),
            ]
        )
    )


class DjangoNodeBasedView(LonaView):
    def handle_request(self, request):
        data = {
            'method': str(request.method),
            'is_valid': None,
            'values': None,
        }

        pre = Pre(
            style={
                'background-color': 'lightgrey',
            },
        )

        if request.method == 'POST':
            form = DjangoForm(
                TestForm,
                request.POST,
                render_as='ul',
                rerender_on_change=False,
            )

            if form.is_valid():
                data['is_valid'] = True
                data['values'] = form.values

            else:
                data['is_valid'] = False

        else:
            form = DjangoForm(
                TestForm,
                render_as='ul',
                rerender_on_change=False,
            )

        pre.set_text(pformat(data))

        return HTML(
            H1('Node based django form'),
            Div(
                Form(
                    form,
                    Submit(),
                    action='.',
                    method='post',
                ),

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
        )
