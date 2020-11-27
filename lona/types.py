class Symbol:
    def __init__(self, name, value=None):
        if not isinstance(name, str):
            raise ValueError('name has to be a string')

        self.name = name.strip().upper()

        if value:
            self.value = value

        else:
            self.value = self.name

    def __eq__(self, other):
        other_value = other

        if isinstance(other_value, Symbol):
            other_value = other_value.value

        if isinstance(other_value, str):
            other_value = other_value.strip().upper()

        return (other_value == self.name or
                other_value == self.value)

    def __repr__(self):
        return self.name

    @classmethod
    def dump_symbol_classes(cls):
        data = {}

        for symbol_class in cls.__subclasses__():
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
