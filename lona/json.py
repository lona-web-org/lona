import json

from lona.types import Symbol


def dumps(data):
    def default(value):
        if isinstance(value, Symbol):
            return value.value

        raise TypeError

    return json.dumps(data, default=default)
