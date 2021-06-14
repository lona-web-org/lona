

Writing A Traditional Form
==========================

When using a {{ link('cookbook/writing-a-lona-form.rst', 'Lona Form') }} the
thread that is running the view is blocked as long as the user holds the
browser tab open. For very interactive or long running views thats no problem,
but for views that only show a big table without any interaction for example
thats very wasteful.

To account for this Lona supports traditional POST requests.

This view creates a simple POST form and releases the thread after showing it.
When the form is submitted, the view gets called again with the post data set
in ``request.POST``.

.. code-block:: python

    from lona.html import HTML, Form, TextInput, Submit, H1
    from lona.view import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            if request.method == 'POST':
                return '<h1>Hello {}</h1>'.format(request.POST['name'])

            return HTML(
                H1('Enter your name'),
                Form(
                    TextInput(name='name'),
                    Submit('Submit'),
                    action='.',
                    method='post',
                ),
            )