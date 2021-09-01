from lona.events.event_types import CHANGE
from lona.html.node import Node


class Option(Node):
    TAG_NAME = 'option'


class Select(Node):
    TAG_NAME = 'select'
    EVENTS = [CHANGE]

    def __init__(self, *args, values=None, disabled=False, bubble_up=False,
                 **kwargs):

        super().__init__(*args, **kwargs)

        self.bubble_up = bubble_up
        if values is not None:
            self.values = values
        self.disabled = disabled

    def handle_change(self, input_event):
        with self.lock:
            self.value = input_event.data

            if self.bubble_up:
                return input_event

    # properties ##############################################################
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

    @property
    def values(self):
        with self.lock:
            values = []

            for node in self.nodes:
                if node.tag_name != 'option':
                    continue

                values.append(
                    (node.attributes.get('value', ''),
                     node.get_text(),
                     'selected' in node.attributes, )
                )

            return values

    @values.setter
    def values(self, new_values):
        with self.lock:
            self.clear()

            for i in new_values:
                value, name, selected = (list(i) + [False])[0:3]
                option_node = Option(str(name), value=str(value))

                if selected:
                    option_node.attributes['selected'] = ''

                self.append(option_node)

    @property
    def value(self):
        with self.lock:
            value = []

            for option in self.nodes:
                if 'selected' in option.attributes:
                    value.append(option.attributes['value'])

            if not value and self.nodes:
                option = self.nodes[0]

                value.append(option.attributes['value'])

            if not value:
                return None

            if 'multiple' not in self.attributes:
                value = value.pop()

            return value

    @value.setter
    def value(self, new_value):
        if not isinstance(new_value, list):
            new_value = [new_value]

        with self.lock:
            for option in self.nodes:
                if option.attributes['value'] in new_value:
                    if 'selected' not in option.attributes:
                        option.attributes['selected'] = ''

                else:
                    if 'selected' in option.attributes:
                        option.attributes.pop('selected')
