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


class Mapping:
    def __init__(self, entries=None):
        self.entries = entries or []

    def get_entry(self, key):
        for entry in self.entries:
            if entry[0] == key:
                return entry

    def keys(self):
        return [i[0] for i in self.entries]

    def items(self):
        for entry in self.entries:
            yield entry

    def pop(self, key):
        for entry in self.entries:
            if entry[0] == key:
                self.entries.remove(entry)

                return entry[1]

        raise KeyError(key)

    def copy(self):
        return Mapping(self.entries.copy())

    def __getitem__(self, key):
        entry = self.get_entry(key)

        if not entry:
            raise KeyError(key)

        return entry[1]

    def __setitem__(self, key, value):
        entry = self.get_entry(key)

        if entry:
            entry[1] = value

        else:
            self.entries.append([key, value])

    def __contains__(self, key):
        return bool(self.get_entry(key))

    def __repr__(self):
        d = {}

        for key, value in self.entries:
            d[repr(key)] = value

        return repr(d)
