from enum import Enum
import json

SEPARATORS = (',', ':')


def default(value):
    # this function does not use isinstance() to avoid import loops

    if isinstance(value, Enum):
        return value.value

    if value.__class__.__name__ == 'WidgetData':
        return value._data

    raise TypeError


def dumps(*args, default=default, separators=SEPARATORS, **kwargs):
    return json.dumps(*args, default=default, separators=separators, **kwargs)
