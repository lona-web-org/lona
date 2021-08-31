from lona.events.event_types import CHANGE
from lona.html.node import Node

DEFAULT_INPUT_DELAY = 300


class TextInput(Node):
    TAG_NAME = 'input'
    SELF_CLOSING_TAG = True

    ATTRIBUTES = {
        'type': 'text',
    }

    def __init__(self, value=None, disabled=False, bubble_up=False,
                 input_delay=DEFAULT_INPUT_DELAY, **kwargs):

        super().__init__(**kwargs)

        self.events.add(CHANGE(input_delay))

        self.bubble_up = bubble_up
        self.disabled = disabled

        if value is not None:
            self.value = value

    def handle_change(self, input_event):
        self.attributes.__setitem__(
            'value',
            input_event.data,
            issuer=(input_event.connection, input_event.window_id),
        )

        self.value = input_event.data

        if self.bubble_up:
            return input_event

    # properties ##############################################################
    # value
    @property
    def value(self):
        return self.attributes.get('value', '')

    @value.setter
    def value(self, new_value):
        self.attributes['value'] = new_value

    # disabled
    @property
    def disabled(self):
        return self.attributes.get('disabled', '')

    @disabled.setter
    def disabled(self, new_value):
        with self.lock:
            if new_value:
                self.attributes['disabled'] = True

            elif 'disabled' in self.attributes:
                self.attributes.pop('disabled')


class TextArea(TextInput):
    TAG_NAME = 'textarea'
    SELF_CLOSING_TAG = False
    ATTRIBUTES = {}

    def __repr__(self):
        return self.__str__(
            skip_value=True,
            node_string=self.attributes.get('value', ''),
        )


class CheckBox(TextInput):
    ATTRIBUTES = {
        'type': 'checkbox',
    }

    @property
    def value(self):
        return self.attributes.get('checked', False)

    @value.setter
    def value(self, new_value):
        self.attributes['checked'] = bool(new_value)
