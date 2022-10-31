is_template: False


Integrating A Frontend Library
==============================

This article will show you the steps to take to integrate a frontend
library like
`Bootstrap 5 <https://getbootstrap.com/docs/5.1/getting-started/introduction/>`_
into your Lona project.

There are two ways to integrate a library. You can add it to your project, or
you can package your library into a Python module to make it reusable
(`reference package <https://github.com/lona-web-org/lona-bootstrap-5>`_)


Adding A Frontend Library To Your Project
-----------------------------------------

Adding a frontend library to a Lona on a project basis works like in
traditional web frameworks: You add your static files to a
`static directory </end-user-documentation/frontends.html#loading-static-files>`_
write a `custom frontend template </end-user-documentation/frontends.html#custom-templates>`_
and produce the right HTML.

.. code-block:: text

    your-project/static/
    └── bootstrap-5.1.0-dist
        ├── css
        │   ├── bootstrap.css
        │   ├── bootstrap.css.map
        │   ├── bootstrap-grid.css
        │   ├── bootstrap-grid.css.map
        │   ├── bootstrap-grid.min.css
        │   ├── bootstrap-grid.min.css.map
        │   ├── bootstrap-grid.rtl.css
        │   ├── bootstrap-grid.rtl.css.map
        │   ├── bootstrap-grid.rtl.min.css
        │   ├── bootstrap-grid.rtl.min.css.map
        │   ├── bootstrap.min.css
        │   ├── bootstrap.min.css.map
        │   ├── bootstrap-reboot.css
        │   ├── bootstrap-reboot.css.map
        │   ├── bootstrap-reboot.min.css
        │   ├── bootstrap-reboot.min.css.map
        │   ├── bootstrap-reboot.rtl.css
        │   ├── bootstrap-reboot.rtl.css.map
        │   ├── bootstrap-reboot.rtl.min.css
        │   ├── bootstrap-reboot.rtl.min.css.map
        │   ├── bootstrap.rtl.css
        │   ├── bootstrap.rtl.css.map
        │   ├── bootstrap.rtl.min.css
        │   ├── bootstrap.rtl.min.css.map
        │   ├── bootstrap-utilities.css
        │   ├── bootstrap-utilities.css.map
        │   ├── bootstrap-utilities.min.css
        │   ├── bootstrap-utilities.min.css.map
        │   ├── bootstrap-utilities.rtl.css
        │   ├── bootstrap-utilities.rtl.css.map
        │   ├── bootstrap-utilities.rtl.min.css
        │   └── bootstrap-utilities.rtl.min.css.map
        └── js
            ├── bootstrap.bundle.js
            ├── bootstrap.bundle.js.map
            ├── bootstrap.bundle.min.js
            ├── bootstrap.bundle.min.js.map
            ├── bootstrap.esm.js
            ├── bootstrap.esm.js.map
            ├── bootstrap.esm.min.js
            ├── bootstrap.esm.min.js.map
            ├── bootstrap.js
            ├── bootstrap.js.map
            ├── bootstrap.min.js
            └── bootstrap.min.js.map

.. code-block:: html

    <!-- templates/lona/frontend.html -->
    <html>
        <head>
            <meta charset="utf-8" />
            {{ Lona.load_stylesheets() }} <!- this loads all stylsheets that are part of a Lona node class ->
            <link href="{{ Lona.load_static_file('bootstrap-5.1.0-dist/css/bootstrap.min.css') }}" rel="stylesheet">
        </head>
        <body>
            <!- add your page layout here ->

            <div id="lona"></div> <!- this is the element where all Lona views are rendered in ->

            <!- add your page layout here ->

            {{ Lona.load_scripts() }} <!- this loads the Lona client library and all scripts that ar part of a Lona node class->
            <script>
                var lona_context = new Lona.LonaContext({
                    target: '#lona',
                    title: 'Lona',
                    update_address_bar: true,
                    update_title: true,
                    follow_redirects: true,
                    follow_http_redirects: true,
                });

                lona_context.setup();
            </script>
        </body>
    </html>

.. code-block:: python

    from lona.html import HTML
    from lona import LonaView


    class ProgressBarView(LonaView):
        def handle_request(self, request):
            html = HTML("""
                <h1>Bootstrap 5 Progressbar</h1>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            """)


Packaging A Frontend Library
----------------------------

To package a frontend library with your HTML nodes, you have to register them
in ``Node.STATIC_FILES``.

This example shows how a package of Bootstrap 5 buttons would look like.

**More information:** `Adding Javascript And CSS To HTML Nodes </end-user-documentation/html.html#adding-javascript-and-css-to-html-nodes>`_

.. code-block:: text

    lona-bootstrap-5/lona_bootstrap_5/
    ├── __init__.py
    ├── buttons.py
    ├── static
    │   ├── bootstrap-5.1.0-dist
    │   │   ├── css
    │   │   │   ├── bootstrap.css
    │   │   │   ├── bootstrap.css.map
    │   │   │   ├── bootstrap-grid.css
    │   │   │   ├── bootstrap-grid.css.map
    │   │   │   ├── bootstrap-grid.min.css
    │   │   │   ├── bootstrap-grid.min.css.map
    │   │   │   ├── bootstrap-grid.rtl.css
    │   │   │   ├── bootstrap-grid.rtl.css.map
    │   │   │   ├── bootstrap-grid.rtl.min.css
    │   │   │   ├── bootstrap-grid.rtl.min.css.map
    │   │   │   ├── bootstrap.min.css
    │   │   │   ├── bootstrap.min.css.map
    │   │   │   ├── bootstrap-reboot.css
    │   │   │   ├── bootstrap-reboot.css.map
    │   │   │   ├── bootstrap-reboot.min.css
    │   │   │   ├── bootstrap-reboot.min.css.map
    │   │   │   ├── bootstrap-reboot.rtl.css
    │   │   │   ├── bootstrap-reboot.rtl.css.map
    │   │   │   ├── bootstrap-reboot.rtl.min.css
    │   │   │   ├── bootstrap-reboot.rtl.min.css.map
    │   │   │   ├── bootstrap.rtl.css
    │   │   │   ├── bootstrap.rtl.css.map
    │   │   │   ├── bootstrap.rtl.min.css
    │   │   │   ├── bootstrap.rtl.min.css.map
    │   │   │   ├── bootstrap-utilities.css
    │   │   │   ├── bootstrap-utilities.css.map
    │   │   │   ├── bootstrap-utilities.min.css
    │   │   │   ├── bootstrap-utilities.min.css.map
    │   │   │   ├── bootstrap-utilities.rtl.css
    │   │   │   ├── bootstrap-utilities.rtl.css.map
    │   │   │   ├── bootstrap-utilities.rtl.min.css
    │   │   │   └── bootstrap-utilities.rtl.min.css.map
    │   │   └── js
    │   │       ├── bootstrap.bundle.js
    │   │       ├── bootstrap.bundle.js.map
    │   │       ├── bootstrap.bundle.min.js
    │   │       ├── bootstrap.bundle.min.js.map
    │   │       ├── bootstrap.esm.js
    │   │       ├── bootstrap.esm.js.map
    │   │       ├── bootstrap.esm.min.js
    │   │       ├── bootstrap.esm.min.js.map
    │   │       ├── bootstrap.js
    │   │       ├── bootstrap.js.map
    │   │       ├── bootstrap.min.js
    │   │       └── bootstrap.min.js.map
    │   └── bootstrap5-widgets.js
    └── static_files.py


.. code-block:: python

    # lona-bootstrap-5/lona_bootstrap_5/buttons.py

    from lona.static_files import StyleSheet, Script, SORT_ORDER

    class Button(BaseButton):
        STATIC_FILES = [
            # css files
            StyleSheet(
                name='bootstrap5.css',
                path='static/bootstrap-5.1.0-dist/css/bootstrap.min.css',
                url='bootstrap5.min.css',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            StyleSheet(
                name='bootstrap5.css',
                path='static/bootstrap-5.1.0-dist/css/bootstrap.min.css',
                url='bootstrap5.min.css.map',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,
            ),

            # js files
            Script(
                name='bootstrap5.bundle.js',
                path='static/bootstrap-5.1.0-dist/js/bootstrap.bundle.min.js',
                url='bootstrap5.bundle.min.js',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            Script(
                name='bootstrap5.bundle.js',
                path='static/bootstrap-5.1.0-dist/js/bootstrap.bundle.min.js.map',
                url='bootstrap5.bundle.min.js.map',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,
            ),
        ]



    class PrimaryButton(Button):
        CLASS_LIST = ['btn', 'btn-primary']


    class SecondaryButton(Button):
        CLASS_LIST = ['btn', 'btn-secondary']


    class SuccessButton(Button):
        CLASS_LIST = ['btn', 'btn-success']


    class DangerButton(Button):
        CLASS_LIST = ['btn', 'btn-danger']


    class WarningButton(Button):
        CLASS_LIST = ['btn', 'btn-warning']


    class InfoButton(Button):
        CLASS_LIST = ['btn', 'btn-info']


    class LightButton(Button):
        CLASS_LIST = ['btn', 'btn-light']


    class DarkButton(Button):
        CLASS_LIST = ['btn', 'btn-dark']


    class LinkButton(Button):
        CLASS_LIST = ['btn', 'btn-link']
