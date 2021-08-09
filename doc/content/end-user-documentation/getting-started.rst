

Getting Started
===============

The easiest way to start a Lona project is to use the
`lona-project-template <https://github.com/fscherf/lona-project-template>`_.

.. code-block:: text

    $ git clone github.com/fscherf/lona-project-template
    $ cd lona-project-template
    $ make server

The GNU make target ``server`` sets up a Python virtualenv and starts
``lona-server``. When you open ``http://localhost:8080`` with your browser, you
should see ``Hello World``.


Writing a view
--------------

In this section we will create an interactive view that counts to ten.

.. code-block:: python

    # lona_project/views/count_to_ten.py

    from lona.html import HTML, H1, P, Div
    from lona.view import LonaView


    class CountToTen(LonaView):
        def handle_request(self, request):
            counter = Div('0')

            html = HTML(
                H1('Count To Ten'),
                P('Counter: ', counter),
            )

            for i in range(1, 11):
                counter.set_text(i)
                self.show(html)

                self.sleep(1)

We need to add a route to ``lona_project/routes.py`` that points to our new
view.

.. code-block:: python

    # lona_project/routes.py

    routes = [
        Route('/count-to-ten/', 'views/count_to_ten.py::CountToTen')
        Route('/', 'views/home.py::HomeView'),
    ]

The new view should now accessible on ``http://localhost:8080/count-to-ten/``.

**More information:**
{{ link('end-user-documentation/views.rst', 'Views') }}


Adding HTML and CSS
-------------------

The overall layout of your page gets defined by
``lona_project/templates/lona/frontend.html``. Here you can add a banner,
navigation, a footer and so on. By default the frontend template loads
``lona_project/static/style.css``. You can extend this file or include
more CSS and Javascript stored in ``lona_project/static``.
