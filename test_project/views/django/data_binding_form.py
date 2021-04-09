from pprint import pformat

from django import forms

from lona.contrib.django.forms import DjangoForm
from lona.html import HTML, H1, Div, Pre
from lona.view import LonaView


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


class DjangoDatabindingView(LonaView):
    def handle_request(self, request):
        form = DjangoForm(TestForm, render_as='ul', bubble_up=True)

        pre = Pre(
            style={
                'background-color': 'lightgrey',
            },
        )

        html = HTML(
            H1('Databinding'),
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
            pre.set_text(pformat(form.values))

            request.client.await_input_event(html=html)
