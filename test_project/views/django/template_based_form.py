from django import forms

from lona.view import LonaView


class NameForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=3)


class DjangoTemplateView(LonaView):
    def handle_request(self, request):
        template_string = """
            <h2>Django Forms</h2>

            {% if name %}
                Hello {{ name }}
            {% endif %}

            <form action="." method="post">
                {{ form }}
                <input type="submit" value="Submit">
            </form>
        """

        name = ''

        if request.method == 'POST':
            form = NameForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']

        else:
            form = NameForm()

        return {
            'template_string': template_string,
            'name': name,
            'form': form,
        }
