search_index_weight: -10


Lona Documentation
==================

| Source code: `github.com/lona-web-org/lona <https://github.com/lona-web-org/lona>`_
| Pypi package: `pypi.org/project/lona <https://pypi.org/project/lona>`_


What is Lona?
-------------

Lona is a web application framework, designed to write responsive web apps in
**full** Python.

Web is a solved problem in Python since ages, but traditionally Python handles
only the server side. If you want to have client side interaction like
click events or you want update content live, you have to write an additional
Javascript application.

Lona handles the server side and the client side, and provides a simple,
pythonic API to write self contained views.


.. code-block:: python

    from lona.html import HTML, Button, Div, H1
    from lona import LonaApp, LonaView

    app = LonaApp(__file__)


    @app.route('/')
    class MyView(LonaView):
        def handle_button_click(self, input_event):
            self.message.set_text('Button clicked')

        def handle_request(self, request):
            self.message = Div('Button not clicked')

            html = HTML(
                H1('Click the button!'),
                self.message,
                Button('Click me!', handle_click=self.handle_button_click),
            )

            return html


    app.run(port=8080)

**More information:**
{{ link('end-user-documentation/getting-started.rst', 'Getting Started') }}


How does it work?
-----------------

Lona comes with a Javascript based browser library that speaks a specialized
protocol with the backend.
This protocol specifies messages like "hey frontend, please show $HTML" and
"hey backend, someone clicked on node XY" 
{{ link('basic-concept.rst', 'read more') }}
