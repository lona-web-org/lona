from lona.events.event_types import CHANGE
from lona.html.node import Node


class Option2(Node):
    TAG_NAME = 'option'

    def __init__(
            self,
            *args,
            value='',
            selected=False,
            disabled=False,
            render_value=True,
            **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.render_value = render_value
        self.value = value
        self.selected = selected
        self.disabled = disabled

    def _render_value(self, value):
        return str(value)

    # properties ##############################################################
    # value
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        with self.lock:
            if self.render_value:
                self.attributes['value'] = self._render_value(new_value)

            self._value = new_value

    # selected
    @property
    def selected(self):
        return 'selected' in self.attributes

    @selected.setter
    def selected(self, new_value):
        if new_value:
            self.attributes['selected'] = ''

        else:
            del self.attributes['selected']

    # disabled
    @property
    def disabled(self):
        return 'disabled' in self.attributes

    @disabled.setter
    def disabled(self, new_value):
        if new_value:
            self.attributes['disabled'] = ''

        else:
            del self.attributes['disabled']


class Select2(Node):
    TAG_NAME = 'select'
    EVENTS = [CHANGE]

    def __init__(self, *options, disabled=False, multiple=False,
                 readonly=False, bubble_up=False, **kwargs):

        super().__init__(**kwargs)

        self.options = options
        self.disabled = disabled
        self.multiple = multiple
        self.readonly = readonly
        self.bubble_up = bubble_up

    def handle_input_event(self, input_event):
        if input_event.name != 'change':
            return super().handle_input_event(input_event)

        # select options by index
        selected_option_indexes = input_event.data

        with self.lock:
            for index, option in enumerate(self.options):
                option.selected = index in selected_option_indexes

        # run custom change event handler
        input_event = self.handle_change(input_event)

        if self.bubble_up:
            return input_event

    # select properties #######################################################
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

    # option properties #######################################################
    # options
    @property
    def options(self):
        with self.lock:
            options = ()

            for node in self.nodes:
                if node.tag_name != 'option':
                    continue

                options += (node, )

            return options

    @options.setter
    def options(self, new_options):
        with self.lock:
            self.nodes.clear()

            if not isinstance(new_options, (list, tuple)):
                new_options = [new_options]

            for option in new_options:
                self.add_option(option)

    # selected options
    @property
    def selected_options(self):
        with self.lock:
            options = ()

            for option in self.options:
                if not option.selected:
                    continue

                options += (option, )

            if not options and self.options and not self.multiple:
                return (self.options[0], )

            return options

    # value
    @property
    def value(self):
        with self.lock:
            selected_options = self.selected_options
            values = ()

            for option in selected_options:
                values += (option.value, )

            if not self.multiple:
                if not values:
                    options = self.options

                    if options:
                        return self.options[0].value

                    return None

                return values[0]

            return values

    @value.setter
    def value(self, new_value):
        with self.lock:
            if not isinstance(new_value, list):
                new_value = [new_value]

            old_values = self.values

            for value in new_value:
                if value not in old_values:
                    raise RuntimeError(f'unknown value: {value}')

            for option in self.options:
                option.selected = option.value in new_value

    # values
    @property
    def values(self):
        with self.lock:
            values = ()

            for option in self.options:
                values += (option.value, )

            return values

    # helper ##################################################################
    def add_option(self, option):
        with self.lock:
            self.nodes.append(option)

    def remove_option(self, option):
        with self.lock:
            self.nodes.remove(option)

    def clear_options(self):
        with self.lock:
            for option in self.options:
                option.remove()

    def select_all(self):
        with self.lock:
            for option in self.options:
                option.selected = True

    def select_none(self):
        with self.lock:
            for option in self.options:
                option.selected = False
