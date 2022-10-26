from __future__ import annotations

from typing import Any
import contextlib

from lona.events.event_types import CHANGE
from lona.html.node import Node

DEFAULT_INPUT_DELAY = 300


class TextInput(Node):
    TAG_NAME = 'input'
    SELF_CLOSING_TAG = True
    INPUT_ATTRIBUTE_NAME = 'value'

    ATTRIBUTES = {
        'type': 'text',
    }

    def __init__(self, value='', disabled=False, readonly=False,
                 bubble_up=False, input_delay=DEFAULT_INPUT_DELAY, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.disabled = disabled
        self.readonly = readonly
        self.bubble_up = bubble_up
        self.events.add(CHANGE(input_delay))

    def _check_validity(self):
        pass

    def handle_input_event(self, input_event):
        # Data binding nodes catch their own change events and synchronize
        # their internal value. When setting their value, a HTML patch,
        # containing the set value, gets created that gets distributed to all
        # connections that are connected to the runtime. By default the input
        # timeout is set to 300ms. When the user # is typing fast, it can
        # happen that a patch gets applied when the user is still typing,
        # resetting the input to a previous state. For the
        # user it looks like the input looses characters while typing.

        # The solution for this problem is to don't send patches back to users
        # who issued them.

        if input_event.name == 'change':
            self.attributes.__setitem__(
                self.INPUT_ATTRIBUTE_NAME,
                input_event.data,
                issuer=(input_event.connection, input_event.window_id),
            )

            self._check_validity()

            input_event = self.handle_change(input_event)

            if self.bubble_up:
                return input_event

        else:
            return super().handle_input_event(input_event)

    # properties ##############################################################
    # value
    @property
    def value(self):
        return self.attributes.get(self.INPUT_ATTRIBUTE_NAME, '')

    @value.setter
    def value(self, new_value):
        self.attributes[self.INPUT_ATTRIBUTE_NAME] = new_value

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


class TextArea(TextInput):
    TAG_NAME = 'textarea'
    SELF_CLOSING_TAG = False
    ATTRIBUTES: dict[str, str] = {}

    def __repr__(self):
        return self.__str__(
            skip_value=True,
            node_string=self.attributes.get('value', ''),
        )


class CheckBox(TextInput):
    INPUT_ATTRIBUTE_NAME = 'checked'
    ATTRIBUTES = {
        'type': 'checkbox',
    }

    def __init__(self, value=False, disabled=False, readonly=False,
                 bubble_up=False, **kwargs):

        super().__init__(value, disabled, readonly, bubble_up, **kwargs)

        if 'input_delay' not in kwargs:
            self.events = [CHANGE]

    @property
    def value(self) -> bool:
        value = self.attributes.get(self.INPUT_ATTRIBUTE_NAME, False)

        if value == '':  # is possible after parsing HTML string
            return True

        return bool(value)

    @value.setter
    def value(self, new_value: bool) -> None:
        if not isinstance(new_value, bool):
            raise TypeError('value is a boolean property')

        # Don't need to remove `checked` attribute if False because
        # it is a special property and is handled differently by js client
        # (search for `property_names` in /lona/client)
        self.attributes[self.INPUT_ATTRIBUTE_NAME] = new_value


class NumberInput(TextInput):
    ATTRIBUTES = {
        'type': 'number',
    }

    def __init__(
            self,
            value: None | float = None,
            min: None | float = None,
            max: None | float = None,
            step: None | float = None,
            disabled: bool = False,
            readonly: bool = False,
            bubble_up: bool = False,
            input_delay: int = DEFAULT_INPUT_DELAY,
            **kwargs: Any,
    ) -> None:

        super().__init__(
            value=value,
            disabled=disabled,
            readonly=readonly,
            bubble_up=bubble_up,
            input_delay=input_delay,
            **kwargs,
        )

        self.min = min
        self.max = max
        self.step = step

    def _get_raw_value(self) -> str:
        return str(self.attributes.get(self.INPUT_ATTRIBUTE_NAME, ''))

    def _get_value(self) -> float | None:
        raw_value = self._get_raw_value()

        with contextlib.suppress(ValueError):
            return float(raw_value)

        return None

    def _check_validity(self) -> None:
        value = self._get_value()

        if not isinstance(value, float):
            self._valid = False

            return

        if ((self.min is not None and value < self.min) or
                (self.max is not None and value > self.max) or
                (self.step is not None and
                    (value-(self.min or 0)) % self.step) != 0):  # NOQA: FS001

            self._valid = False

            return

        self._valid = True

    # properties ##############################################################
    # valid
    @property
    def valid(self) -> bool:
        return self._valid

    # raw_value
    @property
    def raw_value(self) -> str:
        return self._get_raw_value()

    # value
    @property
    def value(self) -> None | float:
        return self._get_value()

    @value.setter
    def value(self, new_value: str | float | None) -> None:
        if new_value is None:
            self.attributes[self.INPUT_ATTRIBUTE_NAME] = ''

        else:
            self.attributes[self.INPUT_ATTRIBUTE_NAME] = str(new_value)

        self._check_validity()

    # min
    @property
    def min(self) -> None | float:
        value = self.attributes.get('min', None)

        if value is not None:
            with contextlib.suppress(ValueError):
                return float(value)

        return None

    @min.setter
    def min(self, new_value: None | float) -> None:
        if new_value is not None and not isinstance(new_value, (int, float)):
            raise TypeError('min should be None, int or float')

        if new_value is None:
            del self.attributes['min']

        else:
            self.attributes['min'] = new_value

        self._check_validity()

    # max
    @property
    def max(self) -> None | float:
        value = self.attributes.get('max', None)

        if value is not None:
            with contextlib.suppress(ValueError):
                return float(value)

        return None

    @max.setter
    def max(self, new_value: None | float) -> None:
        if new_value is not None and not isinstance(new_value, (int, float)):
            raise TypeError('max should be None, int or float')

        if new_value is None:
            del self.attributes['max']

        else:
            self.attributes['max'] = new_value

        self._check_validity()

    # step
    @property
    def step(self) -> None | float:
        value = self.attributes.get('step', None)

        if value is not None:
            with contextlib.suppress(ValueError):
                return float(value)

        return None

    @step.setter
    def step(self, new_value: None | float) -> None:
        if new_value is not None and not isinstance(new_value, (int, float)):
            raise TypeError('step should be None, int or float')

        if new_value is None:
            del self.attributes['step']

        else:
            self.attributes['step'] = new_value

        self._check_validity()
