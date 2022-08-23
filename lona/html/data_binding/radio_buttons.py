from __future__ import annotations

from lona.events.event_types import CHANGE
from lona.html.widget import Widget
from lona.html.node import Node


class RadioButton(Node):
    TAG_NAME = 'input'
    SELF_CLOSING_TAG = True

    ATTRIBUTES = {
        'type': 'radio',
    }

    def __init__(self, name='', value='', disabled=False, readonly=False,
                 bubble_up=True, **kwargs):

        super().__init__(**kwargs)

        self.name = name
        self.value = value
        self.disabled = disabled
        self.readonly = readonly
        self.bubble_up = bubble_up

        self.events.add(CHANGE)

    def handle_input_event(self, input_event):
        if input_event.name == 'change':
            self.checked = input_event.data

        if self.bubble_up:
            return input_event

    def _deselect_associated_radio_buttons(self) -> None:
        with self.lock:

            # find radio button root
            root = self.closest('form')

            if not root:
                root = self.root

            # find associated radio buttons by name
            radio_buttons = root.query_selector_all('input[type=radio]')

            for radio_button in radio_buttons:
                if radio_button == self:
                    continue

                if radio_button.name != self.name:
                    continue

                radio_button.checked = False

    # properties ##############################################################
    # name
    @property
    def name(self):
        return self.attributes.get('name', '')

    @name.setter
    def name(self, new_value):
        self.attributes['name'] = new_value

    # value
    @property
    def value(self):
        return self.attributes.get('value', '')

    @value.setter
    def value(self, new_value):
        self.attributes['value'] = new_value

    # checked
    @property
    def checked(self) -> bool:
        return 'checked' in self.attributes

    @checked.setter
    def checked(self, new_value):
        with self.lock:
            if new_value:
                self.attributes['checked'] = ''
                self._deselect_associated_radio_buttons()

            else:
                del self.attributes['checked']

    # disabled
    @property
    def disabled(self):
        return 'disabled' in self.attributes

    @disabled.setter
    def disabled(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('disabled is a boolean property')

        if new_value:
            self.attributes['disabled'] = ''

        else:
            del self.attributes['disabled']


class RadioButtonGroup(Widget):
    def __init__(self, *nodes, name, bubble_up=False):
        self.nodes = [*nodes]
        self.name = name
        self.bubble_up = bubble_up

    def handle_input_event(self, input_event):
        if(input_event.name != 'change' or
           not isinstance(input_event.node, RadioButton)):

            return input_event

        if self.bubble_up:
            input_event.data = input_event.node.value

            return input_event

    def _iter_radio_buttons(self, check_name=True):
        for radio_button in self.query_selector_all('input[type=radio]'):
            if check_name and radio_button.name != self.name:
                continue

            yield radio_button

    # properties ##############################################################
    # name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        with self.lock:
            self._name = new_name

            for radio_button in self._iter_radio_buttons(check_name=False):
                radio_button.name = new_name

    # value
    @property
    def value(self):
        with self.lock:
            for radio_button in self._iter_radio_buttons(check_name=True):
                if radio_button.checked:
                    return radio_button.value

    @value.setter
    def value(self, new_value):
        with self.lock:
            for radio_button in self._iter_radio_buttons(check_name=True):
                radio_button.checked = radio_button.value == new_value

    # values
    @property
    def values(self):
        values = []

        with self.lock:
            for radio_button in self._iter_radio_buttons(check_name=True):
                values.append(radio_button.value)

        return values
