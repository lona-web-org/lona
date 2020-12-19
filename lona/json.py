import json

from lona.html.widget_data import WidgetData
from lona.types import Symbol

SEPARATORS = (',', ':')


def default(value):
    if isinstance(value, Symbol):
        return value.value

    if isinstance(value, WidgetData):
        return value._data

    raise TypeError


def dumps(*args, default=default, separators=SEPARATORS, **kwargs):
    return json.dumps(*args, default=default, separators=separators, **kwargs)
