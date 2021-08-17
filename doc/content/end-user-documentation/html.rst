is_template: False


HTML API
========

Nodes
-----

In Lona every HTML element is represented as a python object, derived from
``lona.html.Node``.

.. code-block:: python

    from lona.html import Div, H1

    div = Div(
        H1('Hello World'),
        Div('Foo Bar Baz'),
    )

.. code-block:: html

	<div data-lona-node-id="173908150026599">
	  <h1 data-lona-node-id="173908149497883">
		Hello World
	  </h1>
	  <div data-lona-node-id="173908149853937">
		Foo Bar Baz
	  </div>
	</div>


Sub Nodes
~~~~~~~~~

Internally nodes and subnodes behave like python lists and implement all common
list interfaces and methods.

.. code-block:: python

    from lona.html import Div

    >>> div = Div(Div('foo'), Div('bar'))
    >>> div
    <div data-lona-node-id="65286584612039">
        <div data-lona-node-id="65286584010206">
            foo
        </div>
        <div data-lona-node-id="65286584292299">
            bar
        </div>
    </div>

    >>> div.nodes
    <NodeList([<div data-lona-node-id="65286584010206">
        foo
    </div>, <div data-lona-node-id="65286584292299">
        bar
    </div>]))>

    >>> div[0]  # or div.nodes[0]
    <div data-lona-node-id="65286584010206">
        foo
    </div>


Using HTML Strings
~~~~~~~~~~~~~~~~~~

To initialize an HTML tree you can use ``lona.html.HTML``. When
``lona.html.HTML`` gets a HTML string passed in that does not start with ``\``,
the string gets parsed and converted into ``lona.html.Node`` objects.
The resulting tree behaves like a normal Lona HTML tree.

.. code-block:: python

    from lona.html import HTML

    >>> html = HTML('<h1>Hello World</h1><p>Lorem Ipsum</p>')
    >>> html
    <h1 data-lona-node-id="66513259465059">
        Hello World
    </h1>
    <p data-lona-node-id="66513260451573">
        Lorem Ipsum
    </p>


Attributes
~~~~~~~~~~

.. code-block:: python

    from lona.html import Div

    div = Div(foo='bar')

.. code-block:: html

    <div data-lona-node-id="174102029578147" id="bar"></div>

.. code-block:: python

    >>> div.attributes['foo']
    'bar'
    >>> div.attributes['foo'] = 'foo'
    >>> div.attributes['foo']
    'foo'


ID / Class List
~~~~~~~~~~~~~~~

.. code-block:: python

    from lona.html import Div

    div = Div(_id='foo bar baz')
    div = Div(_id=['foo', 'bar' 'baz'])

.. code-block:: html

    <div data-lona-node-id="174102029578147" id="foo bar baz"></div>


Style
~~~~~

.. code-block:: python

    from lona.html import Div

    div = Div(_style={'color': 'red'})
    div.style['background-color'] = 'blue'


.. code-block:: html

    <div data-lona-node-id="182311158684648" style="color: red; background-color: blue"></div>


Adding Custom Nodes
~~~~~~~~~~~~~~~~~~~

To add a new node class you have to inherit from ``lona.html.Node``.

.. code-block:: python

    from lona.html import Node, CLICK


    class BootstrapButton(Node):
        TAG_NAME = 'button'
        SELF_CLOSING_TAG = False
        ID_LIST = []
        CLASS_LIST = ['btn', 'btn-primary']
        STYLE = {}
        ATTRIBUTES = {}
        EVENTS = [CLICK]


Extending Nodes
~~~~~~~~~~~~~~~

.. code-block:: python

    from lona.html import Button


    class BootstrapButton(Button):
        CLASS_LIST = ['btn', 'btn-primary']


Inputs
~~~~~~

To receive input events, the client has to be aware which of your nodes should
produce input events. There are two different input event types ``CLICK`` and
``CHANGE``.

.. code-block:: python

    from lona.html import Div, CLICK

    div = Div(events=[CLICK])

    div2 = Div()
    div2.events.add(CLICK)

.. code-block:: html

    <div data-lona-node-id="182495819713343" data-lona-events="301"></div>

Inputs handle their ``CHANGE`` events internally. When the client sends a
``CHANGE`` event ``Input.value`` gets set, and the event does not get passed to
the next event handler. When ``bubble_up`` is set, input events get handled and
passed further.


Button
""""""

.. code-block:: python

    from lona.html import Button

    Button('Click me!')
    Button('Click me!', _id='foo', _style={'color': 'red'})

**Button Attributes:**

.. table::

    ^Name       ^Description
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes



TextInput / TextArea
""""""""""""""""""""

.. code-block:: python

    from lona.html import TextInput, TextArea

    TextInput()
    TextInput(value='foo', _id='bar', _style={'color': 'red'})

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |value            |None               |(Str,None) Initial value
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) Accepts input
    |input_delay      |300                |(Int) Input delay in milliseconds
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**input_delay:** When ``input_delay`` is set to ``0``, the Javascript client
uses ``onchange`` events. This means the change event gets send when the text
input looses focus or the user hits enter after changing the input. When
``input_delay`` is set to an integer higher than ``0`` the Javascript client
uses ``oninput`` events with ``input_delay`` as timeout.

**Attributes:**

.. table::

    ^Name       ^Description
    |value      |(Str) Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


CheckBox
""""""""

.. code-block:: python

    from lona.html import Checkbox

    CheckBox()
    CheckBox(value=True, _id='bar')


**Attributes:**

.. table::

    ^Name       ^Description
    |value      |(Bool) Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


Select
""""""

.. code-block:: python

    from lona.html import Select

    CheckBox([
        # value, label, is_selected
        ('foo', 'Foo', True),
        ('bar', 'Bar', False),
    ])

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |values           |None               |(List of Tuples) Initial values
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) Accepts input
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**Attributes:**

.. table::

    ^Name       ^Description
    |values     |(List of Tuples) All options
    |value      |Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


Widgets
-------

Widgets are a collections of Nodes that are used to encapsulate logic and input
event handling.

.. code-block:: python

    from lona.html import Widget, Span


    class Counter(Widget):
        def __init__(self, initial_value=0):
            self.nodes = [
                Span(initial_value),
            ]

        def set_value(self, new_value):
            self.nodes[0].set_text(new_value)


Handling Input Events
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from lona.html import Widget, Div, Span, Button


    class Counter(Widget):
        def __init__(self, initial_value=0):
            self.counter = initial_value

            self.counter_label = Span(str(self.counter))
            self.inc_button = Button('+')
            self.dec_button = Button('-')

            self.nodes = [
                Div(
                    self.counter_label,
                    self.inc_button,
                    self.dec_button,
                ),
            ]

        def handle_input_event(self, input_event):
            if input_event.node is self.inc_button:
                self.counter = self.counter + 1
                self.counter_label.set_text(str(self.counter))

            elif input_event.node is self.dec_button:
                self.counter = self.counter - 1
                self.counter_label.set_text(str(self.counter))

            else:
                return input_event


Event Bubbling
""""""""""""""

When an input event gets issued by the frontend, Lona runs all Widget
input event handler from the innermost to the outermost until one of them
does not return the event. In this case the event is regarded as handled.
If all handler return the event ``LonaView.handle_input_event()`` gets to
handle the event.

.. code-block:: python

    MyWidget(  # last
        MyWidget(  # second
            MyWidget(  # first
                Button('Click me!'),
            ),
        ),
    )


Frontend Widgets
~~~~~~~~~~~~~~~~

Widgets can define a Javascript based frontend widget, to include client side
code. This is useful to integrate with third party Javascript libraries.

To communicate between the backend widget and the frontend widget, the backend
can set its state in ``Widget.state``, a dict like object, and the frontend
can issue events with custom data.

.. code-block:: python

    # my_widget.py

    from lona.static_files import Script
    from lona.html import Widget, Div

    class MyWidget(Widget):
        FRONTEND_WIDGET_CLASS = 'MyFrontendWidget'

        STATIC_FILES = [
            # the path is always relative to the current file
            Script(name='MyFrontendWidget', path='my_frontend_widget.js'),
        ]

        def __init__(self):
            self.nodes = [
                Div('foo'),
            ]

            self.data = {'foo': 'bar'}


.. code-block:: javascript

    // my_frontend_widget.js

    function MyFrontendWidget(lona_window) {
        this.lona_window = lona_window;

        this.setup = function() {
            // gets called when the widget gets initialized

            console.log('setup', this.nodes);
        };

        this.deconstruct = function() {
            // gets called when the widget gets destroyed

            console.log('deconstruct', this.nodes);
        };

        this.data_updated = function() {
            // gets called every time Widget.data gets updated in the backend

            console.log('data updated:', this.data);
        };
    };

    Lona.register_widget_class('MyFrontendWidget', MyFrontendWidget);


Firing Custom Input Events
""""""""""""""""""""""""""

.. code-block:: javascript

    // my_frontend_widget.js

    function MyFrontendWidget(lona_window) {
        this.lona_window = lona_window;

        this.setup = function() {
            this.nodes[0].onclick = function(event) {

                // the node argument is optional and can be undefined
                lona_window.fire_input_event(this.nodes[0], 'custom-event', {foo: 'bar'});
            };
        };


Adding Javascript And CSS To Frontend Widgets
"""""""""""""""""""""""""""""""""""""""""""""

Widgets can include stylesheets and javascript files in ``STATIC_FILES``. This
makes packaging of widgets possible.

To control the include order, ``sort_order`` is used. ``sort_order`` is a
simple integer, but to make the code more readable
``lona.static_files.SORT_ORDER`` is used.


.. code-block:: python

    from lona.static_files import StyleSheet, Script, SORT_ORDER
    from lona.html import Widget, Div

    class ChartJsWidget(Widget):
        STATIC_FILES = [
            # styesheets
            StyleSheet(
                name='chart_css_min',
                path='static/Chart.min.css',
                url='Chart.min.css',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            StyleSheet(
                name='chart_css',
                path='static/Chart.css',
                url='Chart.css',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,  # When link is set to False the given file
                             # gets collected, but not linked. Thats necessary
                             # to make map files possible.
            ),

            # scripts
            Script(
                name='chart_bundle_js_min',
                path='static/Chart.bundle.min.js',
                url='Chart.bundle.min.js',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            Script(
                name='chart_bundle_js',
                path='static/Chart.bundle.js',
                url='Chart.bundle.js',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,
            ),
            Script(
                name='chart_js_widget_js',
                path='static/chart-js-widget.js',
                url='chart-js-widget.js',
                sort_order=SORT_ORDER.LIBRARY,
            ),
        ]

Static files, included in widgets, get included in the frontend template with
template tags.

.. code-block:: django

    {{ Lona.load_scripts() }}
    {{ Lona.load_stylesheets() }}


**More information:** `Frontends <end-user-documentation/frontends.html>`_