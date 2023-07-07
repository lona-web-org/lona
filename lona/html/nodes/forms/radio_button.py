from uuid import uuid1

from lona.html.nodes.forms.inputs import TextInput
from lona.html.nodes.text_content import Div
from lona.html.nodes.forms import Label
from lona.html.node import Node


class RadioButton(TextInput):
    INPUT_ATTRIBUTE_NAME = 'checked'

    ATTRIBUTES = {
        'type': 'radio',
        'name': 'radio',
    }

    def __init__(
            self,
            *args,
            value='',
            bubble_up=True,
            checked=False,
            render_value=True,
            **kwargs,
    ):

        self.render_value = render_value

        super().__init__(*args, bubble_up=bubble_up, **kwargs)

        self.value = value
        self.checked = checked

    def _render_value(self, value):
        return str(value)

    # value
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        with self.lock:
            if self.render_value:
                self.attributes['value'] = self._render_value(new_value)

            self._value = new_value

    # name
    @property
    def name(self):
        return self.attributes['name']

    @name.setter
    def name(self, new_value):
        self.attributes['name'] = new_value

    # checked
    @property
    def checked(self):
        return 'checked' in self.attributes

    @checked.setter
    def checked(self, new_value):
        if new_value:
            self.attributes['checked'] = ''

        else:
            del self.attributes['checked']


class RadioGroup(Node):
    TAG_NAME = 'form'

    def handle_input_event(self, input_event):

        # check if incoming event was fired by a radio button and bubble it
        # up if not
        if input_event.name != 'change':
            return super().handle_input_event(input_event)

        if (not input_event.node or
                input_event.node.tag_name != 'input' or
                input_event.node.attributes.get('type', '') != 'radio'):

            return super().handle_input_event(input_event)

        # uncheck all radio buttons in the same radio group that are unchecked
        # on the client
        with self.lock:
            name = input_event.node.attributes.get('name', '')

            for radio_button in self.radio_buttons:
                if radio_button is input_event.node:
                    continue

                if radio_button.attributes.get('name', '') != name:
                    continue

                # The browser unchecks all previously checked radio buttons
                # in the same radio group autamatically. So we don't need
                # to send a patch to the original issuer of the change event.
                if 'checked' in radio_button.attributes:
                    radio_button.attributes.__delitem__(
                        'checked',
                        issuer=(input_event.connection, input_event.window_id),
                    )

        # patch input_event so `input_event.node.value` and `input_event.data`
        # yield the actual value of the radio group
        input_event.node = self
        input_event.data = self.value

        return super().handle_input_event(input_event)

    @property
    def radio_buttons(self):
        return tuple(self.query_selector_all('input[type=radio]'))

    @property
    def checked_radio_button(self):
        with self.lock:
            for radio_button in self.radio_buttons:
                if radio_button.checked:
                    return radio_button

    # value
    @property
    def value(self):
        checked_radio_button = self.checked_radio_button

        if not checked_radio_button:
            return

        return checked_radio_button.value

    @value.setter
    def value(self, new_value):
        with self.lock:
            radio_buttons = self.radio_buttons

            # check if value is available
            if new_value is not None:
                values = []

                for radio_button in radio_buttons:
                    values.append(radio_button.value)

                if new_value not in values:
                    raise ValueError(
                        f"no radio button with value '{new_value}'",
                    )

            # update all radio button checked state
            for radio_button in radio_buttons:
                radio_button.checked = radio_button.value == new_value

    # values
    @property
    def values(self):
        values = []

        with self.lock:
            for radio_button in self.radio_buttons:
                values.append(radio_button.value)

        return tuple(values)

    def add_button(self, *nodes):

        # string value pair
        if (len(nodes) == 2 and
                isinstance(nodes[0], str) and
                not isinstance(nodes[1], Node)):

            return self.add_button(
                Label(nodes[0]),
                RadioButton(value=nodes[1]),
            )

        # find labels and radio buttons
        helper_node = Div(nodes)

        labels = helper_node.query_selector_all('label')
        buttons = helper_node.query_selector_all('input[type=radio]')

        # attach autogenerated id so the labels get clickable in the browser
        button_id = f'id_{uuid1().hex}'

        for label in labels:
            label.attributes['for'] = button_id

        for button in buttons:
            button.id_list.add(button_id)

        # add all nodes to button group
        self.nodes.extend(nodes)
