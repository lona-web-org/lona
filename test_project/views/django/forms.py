from django import forms


class NameForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100)


def handle_request(request):
    template_string = """
        <h1>Django Forms</h1>

        {% if name %}
            {{ name }}
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
