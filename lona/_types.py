class Symbol:
    _INCLUDE_IN_FRONTEND_LIBRARY = False

    def __init__(self, name, value=None):
        if not isinstance(name, str):
            raise ValueError('name has to be a string')

        self.name = name.strip().upper()

        if value is not None:
            self.value = value

        else:
            self.value = self.name

    def __repr__(self):
        return self.name

    @classmethod
    def dump_symbol_classes(cls):
        data = {}

        for symbol_class in cls.__subclasses__():
            if not symbol_class._INCLUDE_IN_FRONTEND_LIBRARY:
                continue

            class_name = symbol_class.__name__
            data[class_name] = {}

            for name in dir(symbol_class):
                if name.startswith('_'):
                    continue

                attribute = getattr(symbol_class, name)

                if not isinstance(attribute, Symbol):
                    continue

                data[class_name][attribute.name] = attribute.value

        return data

    # comparisons #############################################################
    def __eq__(self, other):
        other_value = other

        if isinstance(other_value, Symbol):
            other_value = other_value.value

        if isinstance(other_value, str):
            other_value = other_value.strip().upper()

        return (other_value == self.name or
                other_value == self.value)

    def _compare(self, other, operator):
        if isinstance(other, Symbol):
            return operator(self.value, other.value)

        return operator(self.value, other)

    def __lt__(self, other):
        return self._compare(other, lambda a, b: a < b)

    def __lte__(self, other):
        return self._compare(other, lambda a, b: a <= b)

    def __gt__(self, other):
        return self._compare(other, lambda a, b: a > b)

    def __gte__(self, other):
        return self._compare(other, lambda a, b: a >= b)
