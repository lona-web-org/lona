.. image:: doc/content/logo.svg
    :alt: Lona logo
    :height: 200px
    :width: 200px
.. image:: https://img.shields.io/pypi/l/lona.svg
    :alt: license MIT
    :target: https://pypi.org/project/lona
.. image:: https://img.shields.io/pypi/pyversions/lona.svg
    :alt: python 3
    :target: https://pypi.org/project/lona
.. image:: https://img.shields.io/pypi/v/lona.svg
    :alt: latest version
    :target: https://pypi.org/project/lona
.. image:: https://github.com/lona-web-org/lona/actions/workflows/ci.yml/badge.svg
    :alt: ci status
    :target: https://github.com/lona-web-org/lona/actions/workflows/ci.yml
.. image:: https://img.shields.io/codecov/c/github/lona-web-org/lona.svg
    :alt: code coverage
    :target: https://codecov.io/gh/lona-web-org/lona/


Lona is a web application framework, designed to write responsive web apps in
**full** Python.

**Demos:** `lona-web.org/demos <https://lona-web.org/demos/index.html>`_

**FAQ:** `lona-web.org/faq <http://lona-web.org/faq.html>`_

**Documentation:** `lona-web.org <http://lona-web.org>`_

**Changelog:** `lona-web.org/changelog <http://lona-web.org/changelog.html>`_

**Reddit:** `reddit.com/r/lona_web_org/ <https://www.reddit.com/r/lona_web_org/>`_

**Discord:** `discord.com/lona-web.org <https://discord.gg/WBf5PVACsj>`_

Web is a solved problem in Python since ages, but traditionally Python handles
only the server side. If you want to have client side interaction like
click events or you want update content live, you have to write an additional
Javascript application.

Lona handles the server side and the client side, and provides a simple,
pythonic API to write self contained views.

.. code-block:: text

    # pip install lona

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


    if __name__ == '__main__':
        app.run(port=8080, live_reload=True)

**More information:**
`Getting Started <http://lona-web.org/tutorial/01-getting-started/index.html>`_


How does it work?
-----------------

Lona comes with a Javascript based browser library that speaks a specialized
protocol with the backend.
This protocol specifies messages like "hey frontend, please show $HTML" and
"hey backend, someone clicked on node XY".

**More information:**
`Basic Concept <https://lona-web.org/basic-concept.html>`_
