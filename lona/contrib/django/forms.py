from copy import deepcopy, copy

from lona.html.parsing import html_string_to_node_list
from lona.html import Widget, CHANGE


class ValueDict:
    def __init__(self, django_form):
        self._django_form = django_form

    def __getattribute__(self, name):
        if name == '_django_form':
            return super().__getattribute__(name)

        attribute = self._django_form._form_values.__getattribute__(name)

        if attribute not in ('clear', 'pop', 'popitem', 'update'):
            return attribute

        if not callable(attribute):
            return attribute

        def wrapper(*args, **kwargs):
            return_value = attribute(*args, **kwargs)

            self._django_form._form_data = deepcopy(
                self._django_form._form_values,
            )

            self._django_form.render()

            return return_value

        return wrapper

    def __getitem__(self, name):
        return self._django_form._form_values[name]

    def __setitem__(self, name, value):
        if not self._django_form._form_data:
            self._django_form._form_data = deepcopy(
                self._django_form._form_values,
            )

        self._django_form._form_data[name] = value

        self._django_form.render()

    def __repr__(self):
        return self._django_form._form_values.__repr__()

    def __str__(self):
        return self._django_form._form_values.__str__()

    def __len__(self):
        return self._django_form._form_values.__len__()

    def __bool__(self):
        return self._django_form._form_values.__bool__()


class DjangoForm(Widget):
    def __init__(self, form_class, *form_args, bubble_up=False,
                 rerender_on_change=True, render_as='', **form_kwargs):

        self._form_class = form_class
        self._form_args = list(deepcopy(form_args))
        self._form_kwargs = deepcopy(form_kwargs)

        self.bubble_up = bubble_up
        self.rerender_on_change = rerender_on_change
        self.render_as = render_as

        self._form_data = None
        self._initial = None

        if len(self._form_args) > 0:
            self._form_data = self._form_args.pop(0)

        if len(self._form_args) >= 4:
            self._initial = self._form_args.pop(3)

        if 'data' in self._form_kwargs:
            self._form_data = self._form_kwargs.pop('data')

        if 'initial' in self._form_kwargs:
            self._initial = self._form_kwargs.pop('initial')

        self.render()

    @property
    def values(self):
        return ValueDict(self)

    @values.setter
    def values(self, new_values):
        self._form_data = new_values

        self.render()

    def is_valid(self):
        self._form_data = deepcopy(self._form_values)
        self.render()

        return self._form.is_valid()

    def render(self):
        # render form
        self._form = self._form_class(
            *deepcopy(self._form_args),
            **{
                'data': deepcopy(self._form_data),
                'initial': deepcopy(self._initial),
                **deepcopy(self._form_kwargs),
            }
        )

        if self.rerender_on_change:
            for field in self._form.fields.values():
                field.widget.attrs['data-lona-events'] = CHANGE.serialize()

        if self.render_as:
            render_method = getattr(self._form, 'as_{}'.format(self.render_as))
            html_string = render_method()

        else:
            html_string = str(self._form)

        self.nodes = html_string_to_node_list(html_string)

        # set values
        self._form_values = {}

        for field_name, field in self._form.fields.items():
            self._form_values[field_name] = copy(field.initial)

        for field_name, value in self._form.initial.items():
            self._form_values[field_name] = copy(value)

        for field_name, value in (self._form_data or {}).items():
            self._form_values[field_name] = copy(value)

    def handle_input_event(self, input_event):
        if not self._form_data:
            self._form_data = deepcopy(self._form_values)

        field_name = input_event.node.attributes['name']
        self._form_data[field_name] = input_event.data

        if self.rerender_on_change:
            self.render()

        if self.bubble_up:
            return input_event
