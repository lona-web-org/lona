from copy import copy

from lona.html.nodes import SelectNode, OptionNode, Widget
from lona.events.event_types import CHANGE


class Select(Widget):
    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}
    ATTRIBUTES = {}

    def __init__(self, values=[], disabled=False, bubble_up=False,
                 **select_kwargs):

        self.bubble_up = bubble_up

        self.select_node = SelectNode(**self.gen_node_args(**select_kwargs))
        self.select_node.events.add(CHANGE)

        self.nodes = [
            self.select_node,
        ]

        self.values = values

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

    def handle_input_event(self, input_event):
        with self.lock:
            self.value = input_event.data

            if self.bubble_up:
                return input_event

    @property
    def disabled(self):
        return self.select_nodes.attributes.get('disabled', '')

    @disabled.setter
    def disabled(self, new_value):
        with self.lock:
            if new_value:
                self.select_node.attributes['disabled'] = True

            elif 'disabled' in self.select_node.attributes:
                self.select_node.attributes.pop('disabled')

    @property
    def values(self):
        with self.lock:
            return self._values

    @values.setter
    def values(self, new_values):
        with self.lock:
            self._values = []
            self.select_node.clear()

            for i in new_values:
                value, name, selected = (list(i) + [False])[0:3]
                option_node = OptionNode(str(name), value=str(value))

                if selected:
                    option_node.attributes['selected'] = ''

                self.select_node.append(option_node)

                self._values.append(
                    (value, name, ),
                )

    @property
    def value(self):
        with self.lock:
            value = []

            for option in self.select_node.nodes:
                if 'selected' in option.attributes:
                    value.append(option.attributes['value'])

            if not value and self.select_node.nodes:
                option = self.select_node.nodes[0]

                value.append(option.attributes['value'])

            if not value:
                return None

            if 'multiple' not in self.select_node.attributes:
                value = value.pop()

            return value

    @value.setter
    def value(self, new_value):
        if not isinstance(new_value, list):
            new_value = [new_value]

        with self.lock:
            for option in self.select_node.nodes:
                if option.attributes['value'] in new_value:
                    if 'selected' not in option.attributes:
                        option.attributes['selected'] = ''

                else:
                    if 'selected' in option.attributes:
                        option.attributes.pop('selected')

    # input node properties
    # id
    @property
    def id_list(self):
        return self.select_node.id_list

    @id_list.setter
    def id_list(self, new_value):
        self.select_node.id_list = new_value

    # class
    @property
    def class_list(self):
        return self.select_node.class_list

    @class_list.setter
    def class_list(self, new_value):
        self.select_node.class_list = new_value

    # style
    @property
    def style(self):
        return self.select_node.style

    @style.setter
    def style(self, new_value):
        self.select_node.style = new_value

    # attributes
    @property
    def attributes(self):
        return self.select_node.attributes

    @attributes.setter
    def attributes(self, new_value):
        self.select_node.attributes = new_value

    # ignore
    @property
    def ignore(self):
        return self.select_node.ignore

    @ignore.setter
    def ignore(self, new_value):
        self.select_node.ignore = new_value

    # events
    @property
    def events(self):
        return self.select_node.events

    @events.setter
    def events(self, new_value):
        self.select_node.events = new_value

    # helper
    @property
    def has_id(self):
        return self.select_node.has_id

    @property
    def has_class(self):
        return self.select_node.has_class
