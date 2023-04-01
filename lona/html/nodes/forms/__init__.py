from lona.events.event_types import CLICK
from lona.html.node import Node


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


class Datalist(Node):
    # TODO: remove in 2.0

    TAG_NAME = 'datalist'


class DataList(Node):
    TAG_NAME = 'datalist'


class Fieldset(Node):
    # TODO: remove in 2.0

    TAG_NAME = 'fieldset'


class FieldSet(Node):
    TAG_NAME = 'fieldset'


class Form(Node):
    TAG_NAME = 'form'


class Label(Node):
    TAG_NAME = 'label'


class Legend(Node):
    TAG_NAME = 'legend'


class Meter(Node):
    TAG_NAME = 'meter'


class OptGroup(Node):
    TAG_NAME = 'optgroup'


class Output(Node):
    TAG_NAME = 'output'


class Progress(Node):
    TAG_NAME = 'progress'
