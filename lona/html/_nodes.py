from lona.events.event_types import CLICK
from lona.html.node import Node


# inputs ######################################################################
class Form(Node):
    TAG_NAME = 'form'


class Fieldset(Node):
    TAG_NAME = 'fieldset'


class Label(Node):
    TAG_NAME = 'label'


class Button(Node):
    TAG_NAME = 'button'
    EVENTS = [CLICK]

    def __init__(self, *args, disabled=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled = disabled

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


class Submit(Node):
    TAG_NAME = 'input'
    SELF_CLOSING_TAG = True

    ATTRIBUTES = {
        'type': 'submit',
        'value': 'Submit',
    }
