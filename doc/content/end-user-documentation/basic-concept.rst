

Basic Concept
=============

Lets say you have view that counts to ten:

.. code-block:: python

    # views/count_to_ten.py

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

and the URL to this view is ``/count-to-ten/``

.. code-block:: python

    # routes.py

    routes = [
        Route('/count-to-ten/', 'views/count_to_ten.py::CountToTen')
    ]

When you open ``http://localhost:8080/count-to-ten/`` with your browser, your
view gets not started directly, but Lona starts your
{{ link('end-user-documentation/frontends.rst', 'frontend') }} view. This view
is supposed to serve the basic layout of your page (banner, navigation, footer
and so on) and the Lona Javascript client.

The Javascript client then opens a Websocket connection to the server and sends
the message ``lona:[1,null,101,["http://localhost:8080/count-to-ten/",null]]``.

Lona will then start your view and will send the HTML given to ``show()`` in
a similar message. All Lona messages are JSON encoded, the payload of the
message will look like this:

.. code-block:: text

	[WIDGET,
	 '663758909164540',
	 '',
	 [[NODE,
	   '663758908759614',
	   'h1',
	   [],
	   [],
	   {},
	   {},
	   [[TEXT_NODE, '663758908791192', 'Count To Ten']]],
	  [NODE,
	   '663758908960048',
	   'p',
	   [],
	   [],
	   {},
	   {},
	   [[TEXT_NODE, '663758908983761', 'Counter: '],
		[NODE,
		 '663758909061401',
		 'div',
		 [],
		 [],
		 {},
		 {},
		 [[TEXT_NODE, '663788860494138', '0']]]]]],
	 {}]

The encoded HTML gets rendered to browser readable HTML by the Javascript
client

.. code-block:: html

	<h1 data-lona-node-id="663758908759614">
	  Count To Ten
	</h1>
	<p data-lona-node-id="663758908960048">
	  Counter:
	  <div data-lona-node-id="663758909061401">
		0
	  </div>
	</p>


The HTML gets only send entirely once, because the view
only updates the div named ``counter`` before calling ``show()`` again.

Every Lona HTML node has a unique id stored in ``data-lona-node-id``. When a
node gets updated Lona sends updates only for that specific node.
