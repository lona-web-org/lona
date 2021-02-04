from copy import copy

from lona.html.nodes import SelectNode, OptionNode, Widget


class Select(Widget):
    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}
    ATTRIBUTES = {}

    def __init__(self, values=[], disabled=False, bubble_up=False,
                 **select_kwargs):

        self.bubble_up = bubble_up

        self.select_node = SelectNode(**self.gen_node_args(**select_kwargs))
        self.select_node.changeable = True

        self.nodes = [
            self.select_node,
        ]

        self.values = values

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

    def handle_input_event(self, input_event):
        with self.lock:
            self.value = input_event.data

            if self.bubble_up:
                return input_event

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

            if not value:
                option = self.select_node.nodes[0]

                value.append(option.attributes['value'])

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
