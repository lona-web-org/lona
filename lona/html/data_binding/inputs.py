from copy import copy

from lona.html.nodes import TextAreaNode, InputNode, Widget
from lona.events.event_types import CHANGE

DEFAULT_INPUT_DELAY = 300


class TextInput(Widget):
    NODE_CLASS = InputNode

    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}

    ATTRIBUTES = {
        'type': 'text',
    }

    def __init__(self, disabled=False, bubble_up=False,
                 input_delay=DEFAULT_INPUT_DELAY, **input_kwargs):

        self.bubble_up = bubble_up

        self.input_node = self.gen_input_node(**input_kwargs)

        self.input_node.events.add(CHANGE(input_delay))

        self.nodes = [
            self.input_node,
        ]

        self.disabled = disabled

    def gen_node_args(self, **kwargs):
        id_list = copy(self.ID_LIST)
        class_list = copy(self.CLASS_LIST)
        style = copy(self.STYLE)
        attributes = copy(self.ATTRIBUTES)
        misc_kwargs = {}

        for name, value in kwargs.copy().items():

            # remove underscores from attributes
            # this makes kwargs like '_class' possible to prevent clashes
            # with python grammar
            clean_name = name

            if '_' in clean_name:
                clean_name = clean_name.replace('_', '-')

                if clean_name.startswith('-'):
                    clean_name = clean_name[1:]

            if clean_name == 'id':
                value = kwargs.pop(name)

                if isinstance(value, str):
                    value = value.split(' ')

                id_list.extend(value)

            elif clean_name == 'class':
                value = kwargs.pop(name)

                if isinstance(value, str):
                    value = value.split(' ')

                class_list.extend(value)

            elif clean_name == 'style':
                style.update(kwargs.pop(name))

            elif clean_name == 'attributes':
                attributes.update(kwargs.pop(name))

            else:
                misc_kwargs[name] = value

        return {
            'id': id_list,
            'class': class_list,
            'style': style,
            **attributes,
            **misc_kwargs,
        }

    def gen_input_node(self, **kwargs):
        return self.NODE_CLASS(**self.gen_node_args(**kwargs))

    def handle_input_event(self, input_event):
        self.value = input_event.data

        if self.bubble_up:
            return input_event

    @property
    def value(self):
        return self.input_node.attributes.get('value', '')

    @value.setter
    def value(self, new_value):
        self.input_node.attributes['value'] = new_value

    @property
    def disabled(self):
        return self.input_nodes.attributes.get('disabled', '')

    @disabled.setter
    def disabled(self, new_value):
        with self.lock:
            if new_value:
                self.input_node.attributes['disabled'] = True

            elif 'disabled' in self.input_node.attributes:
                self.input_node.attributes.pop('disabled')


class TextArea(TextInput):
    NODE_CLASS = TextAreaNode


class CheckBox(TextInput):
    ATTRIBUTES = {
        'type': 'checkbox',
    }

    @property
    def value(self):
        return self.input_node.attributes.get('checked', False)

    @value.setter
    def value(self, new_value):
        self.input_node.attributes['checked'] = bool(new_value)
