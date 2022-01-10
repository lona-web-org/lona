from lona.protocol import INPUT_EVENT_TYPE


class EventType:
    def __init__(self, name, symbol):
        self._name = name
        self._symbol = symbol

    def serialize(self):
        return str(self._symbol.value)

    def __repr__(self):
        return self._name

    def __eq__(self, other):
        if not isinstance(other, EventType):
            return False

        return self._symbol == other._symbol


class ChangeEventType:
    def __init__(self, name, symbol, input_delay=0):
        self._name = name
        self._symbol = symbol
        self._input_delay = input_delay

    def __repr__(self):
        if self._input_delay:
            return f'{self._name}(input_delay={self._input_delay})'

        return self._name

    def __call__(self, input_delay=0):
        if not isinstance(input_delay, int):
            raise ValueError('input delay has to be integer')

        return self.__class__(
            name=self._name,
            symbol=self._symbol,
            input_delay=input_delay,
        )

    def serialize(self):
        if self._input_delay:
            return f'{self._symbol.value}:{self._input_delay}'

        return str(self._symbol.value)


CLICK = EventType('CLICK', INPUT_EVENT_TYPE.CLICK)
FOCUS = EventType('FOCUS', INPUT_EVENT_TYPE.FOCUS)
BLUR = EventType('BLUR', INPUT_EVENT_TYPE.BLUR)
CHANGE = ChangeEventType('CHANGE', INPUT_EVENT_TYPE.CHANGE)
