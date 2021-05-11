.. image:: doc/content/logo.svg
    :height: 200px
    :width: 200px
.. image:: https://img.shields.io/pypi/l/lona.svg
    :alt: pypi.org
    :target: https://pypi.org/project/lona
.. image:: https://img.shields.io/travis/com/fscherf/lona/master.svg
    :alt: Travis branch
    :target: https://travis-ci.com/fscherf/lona
.. image:: https://img.shields.io/pypi/pyversions/lona.svg
    :alt: pypi.org
    :target: https://pypi.org/project/lona
.. image:: https://img.shields.io/pypi/v/lona.svg
    :alt: pypi.org
    :target: https://pypi.org/project/lona
.. image:: https://img.shields.io/codecov/c/github/fscherf/lona.svg
    :alt: codecov.io
    :target: https://codecov.io/gh/fscherf/lona/


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
    from lona.view import LonaView


    class MyView(LonaView):
        def handle_request(self, request):
            message = Div('Button not clicked')
            button = Button('Click me!')

            html = HTML(
                H1('Click the button!'),
                message,
                button,
            )

            request.client.show(html)

            # this call blocks until the button was clicked
            input_event = request.client.await_click(button)

            if input_event.node == button:
                message.set_text('Button clicked')

            return html


How does it work?
-----------------

Lona comes with a Javascript based browser library that speaks a specialized
protocol with the backend.
This protocol specifies messages like "hey frontend, please show $HTML" and
"hey backend, someone clicked on node XY".
