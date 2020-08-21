from collections import OrderedDict

from lona.html.nodes import (
    Select as SelectNode,
    Form as FormNode,
    Widget,
    Option,
    Label,
    Input,
    Table,
    Ul,
    Li,
    Tr,
    Td,
)


class OrderedClassMembers(type):
    @classmethod
    def __prepare__(self, name, bases):
        return OrderedDict()

    def __new__(self, name, bases, classdict):
        classdict['__ordered__'] = [
            key for key in classdict.keys()
            if key not in ('__module__', '__qualname__')
        ]

        return type.__new__(self, name, bases, classdict)


class FormField(Widget):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_input_node(self, name):
        return Input(name)

    def setup(self, name):
        # setup input
        self.input = self.get_input_node(name)

        # setup message list
        self.messages = Ul(_class='messages')

        # setup nodes
        label_text = name

        if 'label' in self.kwargs:
            label_text = self.kwargs['label']

        elif self.args:
            label_text = self.args[0]

        self.nodes = [
            Tr(
                Td(Label(label_text)),
                Td(
                    self.messages,
                    self.input,
                ),
            ),
        ]

    # messages ################################################################
    def has_warnings(self):
        for message in self.messages.nodes:
            if 'warning' in message.class_list:
                return True

        return False

    def has_errors(self):
        for message in self.messages.nodes:
            if 'error' in message.class_list:
                return True

        return False

    def add_warning(self, message):
        self.messages.append(
            Li(message, _class='warning'),
        )

    def add_error(self, message):
        self.messages.append(
            Li(message, _class='error'),
        )

    def clear_messages(self):
        self.messages.clear()

    # values ##################################################################
    def get_value(self):
        return self.input.attributes.get('value', None)

    def set_value(self, value):
        self.input.attributes['value'] = value

    # checks ##################################################################
    def check(self):
        pass

    def run_checks(self):
        self.clear_messages()

        return self.check()


class Form(Widget, metaclass=OrderedClassMembers):
    ADD_RESET_BUTTON = True
    ADD_SUBMIT_BUTTON = True

    def __init__(self, initial={}):
        self.initial = initial
        self.clean_values = {}

        # find fields
        self.fields = OrderedDict()

        has_submit_button = False
        has_reset_button = False

        for field_name, field_class in self._find_fields().items():
            if isinstance(field_class, Submit):
                has_submit_button = True

            if isinstance(field_class, Reset):
                has_reset_button = True

            field = field_class.__class__(
                *field_class.args,
                **field_class.kwargs,
            )

            field.setup(field_name)

            self.fields[field_name] = field

        # setup reset and submit button
        self.extra_nodes = []

        if self.ADD_RESET_BUTTON and not has_reset_button:
            reset_button = Reset(value='Reset')
            reset_button.setup('reset')

            self.extra_nodes.append(reset_button)

        if self.ADD_SUBMIT_BUTTON and not has_submit_button:
            submit_button = Submit(value='Submit')
            submit_button.setup('submit')

            self.extra_nodes.append(submit_button)

        # setup nodes
        self.nodes = [
            FormNode(
                Table(
                    *self.fields.values(),
                ),
                *self.extra_nodes,
            ),
        ]

        # populate initial data
        if self.initial:
            self.set_values(self.initial, run_checks=False)

    def _find_fields(self):
        fields = []

        for key in self.__ordered__:
            if key in ('has_errors', ):
                continue

            value = getattr(self, key)

            if not isinstance(value, FormField):
                continue

            fields.append(
                (key, value, )
            )

        return OrderedDict(fields)

    # messages ################################################################
    def has_warnings(self):
        for name, field in self.fields.items():
            if field.has_warnings():
                return True

        return False

    def has_errors(self):
        for name, field in self.fields.items():
            if field.has_errors():
                return True

        return False

    def add_warning(self, field_name, error_message):
        self.fields[field_name].add_error(error_message)

    def add_error(self, field_name, error_message):
        self.fields[field_name].add_error(error_message)

    def clear_messages(self):
        for name, field in self.fields.items():
            field.clear_messages()

    # checks ##################################################################
    def check(self):
        pass

    def run_checks(self):
        self.clean_values = {}

        for name, field in self.fields.items():
            clean_value = field.run_checks()

            if clean_value is None:
                clean_value = field.get_value()

            self.clean_values[name] = clean_value

        return self.check()

    # values ##################################################################
    def set_values(self, data, run_checks=True):
        if run_checks:
            for field_name in self.fields.keys():
                if field_name not in data:
                    data[field_name] = None

        for name, value in data.items():
            field = self.fields[name]
            field.set_value(value)

        if run_checks:
            self.run_checks()

    def get_values(self):
        return self.clean_values

    # event handling ##########################################################
    def on_submit(self, input_event):
        self.clear_messages()
        self.set_values(input_event.data, run_checks=True)

        if not self.has_errors():
            return input_event


# fields ######################################################################
# buttons
class Submit(FormField):
    def get_input_node(self, name):
        return Input(type='submit', name=name)

    def setup(self, name):
        super().setup(name)

        self.nodes = [self.input]


class Reset(FormField):
    def get_input_node(self, name):
        return Input(type='reset', name=name)

    def setup(self, name):
        super().setup(name)

        self.nodes = [self.input]


# inputs
class TextField(FormField):
    def get_input_node(self, name):
        input_args = {
            'type': 'text',
            'name': name,
            'value': self.kwargs.get('default', ''),
        }

        if 'placeholder' in self.kwargs:
            input_args['placeholder'] = self.kwargs['placeholder']

        return Input(**input_args)

    def check(self):
        value = self.get_value()

        if not value:
            return ''

        return str(value)


class PasswordField(TextField):
    def get_input_node(self, name):
        input_node = super().get_input_node(name)
        input_node.attributes['type'] = 'password'

        return input_node


class ColorField(FormField):
    def get_input_node(self, name):
        input_args = {
            'type': 'color',
            'name': name,
            'value': self.kwargs.get('default', ''),
        }

        return Input(**input_args)


class DateField(FormField):
    # TODO: parse type

    def get_input_node(self, name):
        input_args = {
            'type': 'date',
            'name': name,
            'value': self.kwargs.get('default', ''),
        }

        return Input(**input_args)


class WeekField(FormField):
    # TODO: parse type

    def get_input_node(self, name):
        input_args = {
            'type': 'week',
            'name': name,
            'value': self.kwargs.get('default', ''),
        }

        return Input(**input_args)


class TimeField(FormField):
    # TODO: parse type

    def get_input_node(self, name):
        input_args = {
            'type': 'time',
            'name': name,
            'value': self.kwargs.get('default', ''),
        }

        return Input(**input_args)


class CheckboxField(FormField):
    def get_input_node(self, name):
        input_args = {
            'type': 'checkbox',
            'name': name,
        }

        input_node = Input(**input_args)

        if 'default' in self.kwargs and self.kwargs['default']:
            input_node.attributes['checked'] = ''

        return input_node

    def set_value(self, value):
        checked = value or value is not None

        if not checked and 'checked' in self.input.attributes:
            self.input.attributes.pop('checked')

        if checked:
            self.input.attributes['checked'] = ''

    def get_value(self):
        return 'checked' in self.input.attributes


class Select(FormField):
    def get_input_node(self, name):
        input_node = SelectNode(name=name)
        self._choices = {}

        if 'multiple' in self.kwargs and self.kwargs['multiple']:
            input_node.attributes['multiple'] = ''

        if 'choices' in self.kwargs:
            for choice in self.kwargs['choices']:
                value, selected = choice

                option = Option(value, value=value)

                if selected:
                    option.attributes['selected'] = ''

                input_node.nodes.append(option)
                self._choices[value] = option

        return input_node

    def get_value(self):
        value = []

        for name, option in self._choices.items():
            if 'selected' in option.attributes:
                value.append(option.attributes['value'])

        if 'multiple' in self.kwargs and self.kwargs['multiple']:
            return value

        return value[0]

    def set_value(self, value):
        if not isinstance(value, list):
            value = [value]

        # deselect all options for now
        for name, option in self._choices.items():
            if 'selected' in option.attributes:
                option.attributes.pop('selected')

        # select given values
        for i in value:
            self._choices[i].attributes['selected'] = ''
