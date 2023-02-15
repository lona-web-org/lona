is_template: False
search_index_weight: 10


HTML API
========

Nodes
-----

.. note::

    **Changed in 1.11:** Nodes are comparable now

    .. code-block:: python

        >>> Div() == Div()            # True
        >>> Div() is Div()            # False
        >>> Div(a=1) == Div()         # False
        >>> Span() == Div()           # False
        >>> Div(Div()) == Div(Div())  # True

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

Sub nodes can be defined as args, as a list or by using the ``nodes`` keyword.

.. note::

    The list syntax was added in 1.4.1

.. code-block:: python

    from lona.html import Div

    Div(Div('foo'), Div('bar'))

    Div([
        Div('foo'),
        Div('bar'),
    ])

    Div(nodes=[
        Div('foo'),
        Div('bar'),
    ])


Selectors
~~~~~~~~~

To find nodes in big node trees Lona provides a query selector API similar to
Javascript.

``AbstractNode.query_selector()`` returnes the first first matching node in
the node tree. ``AbstractNode.query_selector_all()`` returnes a list of all
matching nodes.

.. code-block:: python

    from lona.html import HTML

    html = HTML("""
        <div>
            <div id="foo">
                Foo
                <div id="bar">Bar</div>
            </div>
        </div>
    """)

    foo = html.query_selector('#foo')
    bar = foo.query_selector('#bar')


Syntax
++++++

.. table::

    ^Example          ^Description
    |"div"            |Selects all nodes with the tag name "div"
    |"div#foo"        |Selects all nodes with the tag name "div" and the id "foo"
    |"div#foo#bar"    |Selects all nodes with the tag name "div" and the ids "foo" and "bar"
    |"#foo"           |Selects all nodes with the id "foo"
    |"#foo#bar"       |Selects all nodes with the ids "foo" and "bar"
    |".foo"           |Selects all nodes with the class "foo"
    |".foo.bar"       |Selects all nodes with the classes "foo" and "bar"
    |"#foo,#bar"      |Selects all nodes with the classes "foo" or "bar"
    |"[foo=bar]"      |Selects all nodes with the attribute "foo" set to "bar"


Closest\(selector\)
+++++++++++++++++++

.. note::

    Added in 1.4.1

``AbstractNode.closest()`` returns the closest parent node that matches the
given selector.

.. code-block:: python

    from lona.html import Table, Tr, Td, A, CLICK

    link = A('click me', href='#', events=[CLICK]

    table = Table(
        Tr(
            Td('Foo'),
            Td('bar'),
            Td(a),
        )
    )

    tr = a.closest('tr')


Using HTML Strings
~~~~~~~~~~~~~~~~~~

.. note::

    Added in 1.5: Support for high level nodes, the keyword
    ``use_high_level_nodes``

To initialize an HTML tree you can use ``lona.html.HTML``. When
``lona.html.HTML`` gets a HTML string passed in that does not start with ``\``,
the string gets parsed and converted into ``lona.html.Node`` objects.
The resulting tree behaves like a normal Lona HTML tree.

``lona.html.HTML`` uses high level nodes from the standard library like
``lona.html.TextInput`` which implement high level methods and properties.
To disable this and parse HTML into blank nodes you can set
``use_high_level_nodes=False``.

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

    <div data-lona-node-id="174102029578147" foo="bar"></div>

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


Helper Methods
~~~~~~~~~~~~~~

Node.hide()
+++++++++++

    Sets ``Node.style['display']`` to ``'none'``.


Node.show()
+++++++++++

    Deletes ``Node.style['display']`` if is set.


Node.set_text(string)
+++++++++++++++++++++

    Resets ``Node.nodes`` to the given string.


Node.get_text()
+++++++++++++++

    Returns a concatenated string of all sub nodes, without HTML syntax.


Links
~~~~~

.. code-block:: python

    from lona.html import A

    # internal link
    A('Internal Link', href='/internal-link/')

    # external link
    A('Lona Documentation', href='https://lona-web.org/', interactive=False)

    # internal link to a non-interactive (or HTTP-pass-through) view that
    # serves a downloadable file. Without "target='_blank'", the browser would
    # try to download the file in the current browser tab, terminating the
    # websocket connection, which would break the currently opened,
    # interactive view.
    A('Internal Download Link', href='/foo.pdf',
      interactive=False, target='_blank')


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


Locking
~~~~~~~

Lona is multithreaded and up to three threads can be involved at the same time
to run a view (more information:
`Resource management </end-user-documentation/views.html#resource-management>`_)

To avoid race conditions between threads you can use
``lona.html.AbstractNode.lock``.

The followwing view implements a counter that gets incremented once a second
in ``handle_request()``. When the decrement button is clicked, the event gets
handled in ``handle_input_event()``. When incrementing and decrementing, the
view reads the current value from the HTML tree, changes it and writes back.
To avoid race conditions, both callbacks lock the HTML tree, before reading
and release it after writing.

.. code-block:: python

    from lona.html import HTML, Div, H1, Button
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            self.counter = Div('0')
            self.button = Button('Decrement Counter')

            self.html = HTML(
                H1('Counter'),
                self.counter,
                self.button,
            )

            while True:

                # increment counter
                with self.html.lock:
                    self.counter.set_text(
                        str(int(self.counter.get_text()) + 1)
                    )

                # show html
                self.show(self.html)
                self.sleep(1)

        def handle_input_event(self, input_event):
            if input_event.node is not self.button:
                return

            # decrement button
            with self.html.lock:
                self.counter.set_text(
                    str(int(self.counter.get_text()) - 1)
                )


State
~~~~~

.. note::

    Added in 1.10

    **Changed in 1.11:** ``Node.state`` now can be initialized using
    ``Node(state={})``

Lona nodes can store state that is not send to the client in
``node.state``. This data store can be used to transport state between
scopes, for example when handling input events.

``node.state`` is thread safe and is coupled with ``node.lock``.

.. code-block:: python

    DATA = [
        ('Alice', 'Alison', 1, ),
        ('Bob', 'Brown', 2, ),
    ]

    class MyLonaView(LonaView):
        def handle_request(self, request):
            # show all entries in DATA
            html = HTML(
                Table(
                    Tr(
                        Th('First Name'),
                        Th('Last Name'),
                    )
                )
            )

            for first_name, last_name, secret_id in DATA:
                tr = Tr(
                    Td(first_name),
                    Td(last_name),
                    events=[CLICK],
                )

                tr.handle_click = self.handle_click_on_tr

                # set secret id
                tr.state['secret_id'] = secret_id

            self.show(html)

        def handle_click_on_tr(self, input_event):
            # retrieve secret id
            secret_id = input_event.node.state['secret_id']

            # remove entry by secret_id
            DATABASE.remove_user(secret_id)


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
++++++

.. code-block:: python

    from lona.html import Button

    Button('Click me!')
    Button('Click me!', _id='foo', _style={'color': 'red'})

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |disabled         |False              |(Bool) sets the HTML attribute "disabled"
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**Attributes:**

.. table::

    ^Name       ^Description
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes



TextInput / TextArea
++++++++++++++++++++

.. note::

    ``readonly`` was added in 1.6

.. code-block:: python

    from lona.html import TextInput, TextArea

    TextInput()
    TextInput(value='foo', _id='bar', _style={'color': 'red'})

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |value            |None               |(Str,None) Initial value
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) sets the HTML attribute "disabled"
    |readonly         |False              |(Bool) Accepts no input, but can be read and selected
    |input_delay      |300                |(Int) Input delay in milliseconds
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**input_delay:** When ``input_delay`` is set to ``0``, the Javascript client
uses ``onchange`` events. This means the change event gets send when the text
input loses focus or the user hits enter after changing the input. When
``input_delay`` is set to an integer greater than ``0``, the Javascript client
uses ``oninput`` events with ``input_delay`` as timeout. The Javascript client
then delays sending input events by ``input_delay`` ms, and newer input events
cancel older, pendings events. This is also known as *debouncing* of input events
in reactive programming.

**Attributes:**

.. table::

    ^Name       ^Description
    |value      |(Str) Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |readonly   |(Bool) Accepts no input, but can be read and selected
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


NumberInput
+++++++++++

.. note::

    Added in 1.8

.. code-block:: python

    from lona.html import NumberInput

    NumberInput()
    NumberInput(min=2, max=8, step=2)

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |value            |None               |(Float,None) Initial value
    |min              |None               |(Float,None) Minimal value
    |max              |None               |(Float,None) Maximal value
    |step             |None               |(Float,None) Valid steps for value
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) sets the HTML attribute "disabled"
    |readonly         |False              |(Bool) Accepts no input, but can be read and selected
    |input_delay      |300                |(Int) Input delay in milliseconds
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**Attributes:**

.. table::

    ^Name       ^Description
    |value      |(Float) Currently set value
    |raw_value  |(Str) Currently raw value set by the user
    |min        |(Float,None) Minimal value
    |max        |(Float,None) Maximal value
    |step       |(Float,None) Valid steps for value
    |valid      |(Bool) value meets all constrains set by min, max and step
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |readonly   |(Bool) Accepts no input, but can be read and selected
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


CheckBox
++++++++

.. code-block:: python

    from lona.html import CheckBox

    CheckBox()
    CheckBox(value=True, _id='bar')

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |value            |False              |(Bool) Initial value
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) sets the HTML attribute "disabled"
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**Attributes:**

.. table::

    ^Name       ^Description
    |value      |(Bool) Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


Select
++++++

.. note::

    ``multiple`` was added in 1.6

.. warning::

    Deprecated since 1.12. Use `Select2 <#id1>`_ instead.


.. code-block:: python

    from lona.html import Select

    Select(
        values=[
            # value, label, is_selected
            ('foo', 'Foo', True),
            ('bar', 'Bar', False),
        ],
    )

**Init Arguments:**

.. table::

    ^Name             ^Default Value      ^Description
    |values           |None               |(List of Tuples) Initial values
    |bubble_up        |False              |(Bool) Pass input events further
    |disabled         |False              |(Bool) sets the HTML attribute "disabled"
    |multiple         |False              |(Bool) Enables multi selection
    |*args            |()                 |Node args
    |**kwargs         |{}                 |Node kwargs

**Attributes:**

.. table::

    ^Name       ^Description
    |values     |(List of Tuples) All options
    |value      |Currently set value
    |disabled   |(Bool) sets the HTML attribute "disabled"
    |multiple   |(Bool) Enables multi selection
    |id_list    |(List) contains all ids
    |class_list |(List) contains all classes
    |style      |(Dict) contains all styling attributes


Select2
+++++++

.. note::

    Added in 1.12


.. code-block:: python

    from lona.html import Select2, Option2

    select2 = Select2(
        Option2('Option 1', value='1'),
        Option2('Option 2', value=2),
        Option2('Option 3', value=3.0, selected=True),
    )

    # disable first option
    select2.options[0].disabled = True

    # select second option by selected property
    select2.options[1].selected = True

    # select second option by value property
    select2.value = 2

A ``Select2`` consist of one or more ``Option2`` objects, which hold
information on value, selection state and disabled state.

``Option2`` objects consist of a label text and a value. The value can be
anything. If ``Option2.render_value`` is set, which is set by default, the
content of ``Option2.value`` gets typecasted to a string and rendered into the
HTML tree. This can be disabled if the actually values of the select shouldn't
be disclosed to end users.

``Select2.value`` returns the value of the option that is currently
selected. If the ``Select2`` is a multi select, ``Select2.value`` returns a
tuple of all selected options values.

An option can be selected by setting ``Select2.value`` to the value of the
option that should be selected, or by setting ``Option2.selected``. If the
select is no multi select, all other options get unselected automatically.

**Select Attributes:**

.. table::

    ^Name              ^Description
    |value             |Value of the currently selected option or tuple of values of selected options
    |values            |(Tuple) tuple of all possible values
    |options           |(Tuple) tuple of all options
    |selected_options  |(Tuple) tuple of all selected options
    |disabled          |(Bool) sets the HTML attribute "disabled"
    |multiple          |(Bool) Enables multi selection
    |id_list           |(List) contains all ids
    |class_list        |(List) contains all classes
    |style             |(Dict) contains all styling attributes

**Option Attributes:**

.. table::

    ^Name              ^Description
    |value             |value of the option
    |selected          |(Bool) sets selection state
    |disabled          |(Bool) sets the HTML attribute "disabled"
    |id_list           |(List) contains all ids
    |class_list        |(List) contains all classes
    |style             |(Dict) contains all styling attributes


Adding Javascript And CSS To HTML Nodes
---------------------------------------

HTML nodes can include stylesheets and javascript files in ``STATIC_FILES``.
This makes packaging of widgets and nodes possible.

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

Static files, included in HTML nodes, get included in the frontend template
with template tags.

.. code-block:: django

    {{ Lona.load_scripts() }}
    {{ Lona.load_stylesheets() }}


**More information:** `Frontends </end-user-documentation/frontends.html>`_


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
++++++++++++++

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

.. note::

    Frontend widget support for ``lona.html.Node`` was added in 1.10.5

Widgets and nodes can define a Javascript based frontend widget, to include
client side code. This is useful to integrate with third party Javascript
libraries.

To communicate between the backend widget and the frontend widget, the backend
can set its state in ``Widget.state``, or in ``Node.widget_data`` a dict like
object, and the frontend can issue events with custom data.

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


.. code-block:: python

    # my_node.py

    from lona.static_files import Script
    from lona.html import Div

    class MyNode(Div):
        WIDGET = 'MyFrontendWidget'

        STATIC_FILES = [
            # the path is always relative to the current file
            Script(name='MyFrontendWidget', path='my_frontend_widget.js'),
        ]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.nodes = [
                Div('foo'),
            ]

            self.widget_data = {'foo': 'bar'}


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
++++++++++++++++++++++++++

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
