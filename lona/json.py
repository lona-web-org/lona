import json

from lona.html.widget_data import WidgetData
from lona.types import Symbol


def dumps(data):
    def default(value):
        if isinstance(value, Symbol):
            return value.value

        if isinstance(value, WidgetData):
            return value._data

        raise TypeError

    return json.dumps(data, default=default)
