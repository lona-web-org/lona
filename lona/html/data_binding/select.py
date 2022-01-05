from lona.events.event_types import CHANGE
from lona.html.node import Node


class Option(Node):
    TAG_NAME = 'option'


class Select(Node):
    TAG_NAME = 'select'
    EVENTS = [CHANGE]

    def __init__(self, *args, values=None, disabled=False, multiple=False,
                 readonly=False, bubble_up=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = values or []
        self.disabled = disabled
        self.multiple = multiple
        self.readonly = readonly
        self.bubble_up = bubble_up

    def handle_input_event(self, input_event):
        if input_event.name == 'change':
            self.value = input_event.data

            input_event = self.handle_change(input_event)

            if self.bubble_up:
                return input_event

        else:
            return super().handle_input_event(input_event)

    # properties ##############################################################
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

    # multiple
    @property
    def multiple(self):
        return 'multiple' in self.attributes

    @multiple.setter
    def multiple(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('multiple is a boolean property')

        if new_value:
            self.attributes['multiple'] = ''

        else:
            del self.attributes['multiple']

    # readonly
    @property
    def readonly(self):
        return 'readonly' in self.attributes

    @readonly.setter
    def readonly(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('readonly is a boolean property')

        if new_value:
            self.attributes['readonly'] = ''

        else:
            del self.attributes['readonly']

    # values
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
                     'selected' in node.attributes),
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

    # value
    @property
    def value(self):
        with self.lock:
            value = []

            for option in self.nodes:
                if 'selected' in option.attributes:
                    value.append(option.attributes['value'])

            if not self.multiple and not value and self.nodes:
                option = self.nodes[0]

                value.append(option.attributes['value'])

            if not value:
                if not self.multiple:
                    return None

                return value

            if not self.multiple:
                value = value.pop()

            return value

    @value.setter
    def value(self, new_value):
        if not isinstance(new_value, list):
            new_value = [new_value]

        with self.lock:
            for option in self.nodes:
                if option.attributes['value'] in new_value:
                    option.attributes['selected'] = ''

                else:
                    del option.attributes['selected']
