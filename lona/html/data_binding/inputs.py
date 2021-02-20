from copy import copy

from lona.html.nodes import InputNode, TextAreaNode
from lona.html import Widget

DEFAULT_INPUT_DELAY = 300


class TextInput(Widget):
    NODE_CLASS = InputNode

    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}

    ATTRIBUTES = {
        'type': 'text',
        'data-lona-input-delay': DEFAULT_INPUT_DELAY,
    }

    def __init__(self, disabled=False, bubble_up=False, **input_kwargs):
        self.bubble_up = bubble_up

        self.input_node = self.gen_input_node(**input_kwargs)

        self.input_node.changeable = True

        self.nodes = [
            self.input_node,
        ]

        self.disabled = disabled

    def gen_node_args(self, **kwargs):
        id_list = copy(self.ID_LIST)
        class_list = copy(self.CLASS_LIST)
        style = copy(self.STYLE)
        attributes = copy(self.ATTRIBUTES)

        if '_id' in kwargs:
            id_list.extend(kwargs.pop('_id'))

        if '_class' in kwargs:
            id_list.extend(kwargs.pop('_class'))

        if 'style' in kwargs:
            style.update(kwargs.pop('style'))

        elif '_style' in kwargs:
            style.update(kwargs.pop('_style'))

        if 'attributes' in kwargs:
            attributes.update(kwargs.pop('attributes'))

        elif '_attributes' in kwargs:
            attributes.update(kwargs.pop('_attributes'))

        return {
            'id': id_list,
            'class': class_list,
            'style': style,
            **attributes,
            **kwargs,
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

    ATTRIBUTES = {
        'data-lona-input-delay': DEFAULT_INPUT_DELAY,
    }


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
