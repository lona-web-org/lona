

Writing A Lona Form
===================

This example defines a simple view with one ``TextInput`` and two ``Button``.
One of the buttons lets the view print the current value of ``text_input``, the
other one resets the value of ``text_input`` to its initial value.

The browser ``CHANGE`` events get handled by ``lona.html.TextInput`` internally.
To get notified when the value is changed set ``bubble_up`` to ``True``.


.. code-block:: python

    from lona.html import HTML, TextInput, Button
    from lona.view import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            initial_value = 'Test'

            # bubble_up is set to False by default and does not have to be
            # set explicitly
            text_input = TextInput(value=initial_value, bubble_up=False)

            html = HTML(
                text_input,
                Button('Print Value', _id='print-value'),
                Button('Reset Value', _id='reset-value'),
            )

            while True:
                self.show(html)
                input_event = self.await_input_event()

                # this only works if bubble_up is set to True
                if input_event.name == 'change':
                    print('text_input.value was changed to: ', text_input.value

                if input_event.node_has_id('print-value'):
                    print('text_input.value: ', text_input.value)

                elif input_event.node_has_id('reset-value'):
                    text_input.value = initial_value