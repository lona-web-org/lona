from copy import deepcopy

from lona.protocol import OPERATION, PATCH_TYPE


def check_value(value):
    if value is None:
        return

    if not isinstance(value, (bool, int, float, str, list, dict)):
        raise ValueError('unsupported type: {}'.format(type(value)))

    if isinstance(value, list):
        for i in value:
            check_value(i)

    if isinstance(value, dict):
        for k, v in value.items():
            check_value(k)
            check_value(v)


class ListOverlay:
    def __init__(self, widget_data, key_path, original_data):
        self._widget_data = widget_data
        self._widget = widget_data._widget
        self._key_path = key_path
        self._original_data = original_data

    def append(self, item):
        check_value(item)

        with self._widget.lock:
            self._original_data.append(item)

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.INSERT,
                payload=[
                    self._key_path,
                    len(self._original_data) - 1,
                    deepcopy(item),
                ],
            )

    def clear(self):
        with self._widget.lock:
            self._original_data.clear()

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.CLEAR,
                payload=[
                    self._key_path,
                ],
            )

    def copy(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.copy(*args, **kwargs)

    def count(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.count(*args, **kwargs)

    def extend(self, items):
        check_value(items)

        with self._widget.lock:
            for item in items:
                self.append(item)

    def index(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.count(*args, **kwargs)

    def insert(self, index, item):
        check_value(item)

        with self._widget.lock:
            self._original_data.insert(index, item)

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.INSERT,
                payload=[
                    self._key_path,
                    self._original_data.index(item),
                    deepcopy(item),
                ],
            )

    def pop(self, index):
        with self._widget.lock:
            item = self._original_data.pop(index)

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.REMOVE,
                payload=[
                    self._key_path,
                    index,
                ],
            )

            return item

    def remove(self, item):
        with self._widget.lock:
            index = 0

            for i in self._original_data:
                if i == item:
                    self._widget.document.add_patch(
                        node_id=self._widget.id,
                        patch_type=PATCH_TYPE.WIDGET_DATA,
                        operation=OPERATION.REMOVE,
                        payload=[
                            self._key_path,
                            index,
                        ],
                    )

                index += 1

            self._original_data.remove(item)

    def reverse(self, *args, **kwargs):
        raise NotImplementedError

    def sort(self, *args, **kwargs):
        raise NotImplementedError

    def __setitem__(self, name, item):
        with self._widget.lock:
            check_value(name)
            check_value(item)

            self._original_data[name] = item

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.SET,
                payload=[
                    self._key_path,
                    name,
                    item,
                ],
            )

    def __getitem__(self, name):
        with self._widget.lock:
            item = self._original_data[name]

            if isinstance(item, list):
                return ListOverlay(
                    widget_data=self._widget_data,
                    key_path=self._key_path + [name],
                    original_data=item,
                )

            if isinstance(item, dict):
                return DictOverlay(
                    widget_data=self._widget_data,
                    key_path=self._key_path + [name],
                    original_data=item,
                )

            return item

    def __delitem__(self, name):
        with self._widget.lock:
            del self._original_data[name]

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.REMOVE,
                payload=[
                    self._key_path,
                    name,
                ],
            )

    def __str__(self, *args, **kwargs):
        with self._widget.lock:
            return str(self._original_data)

    def __repr__(self, *args, **kwargs):
        with self._widget.lock:
            return repr(self._original_data)

    def __len__(self, *args, **kwargs):
        with self._widget.lock:
            return len(self._original_data)

    def __bool__(self, *args, **kwargs):
        with self._widget.lock:
            return bool(self._original_data)


class DictOverlay:
    def __init__(self, widget_data, key_path, original_data):
        self._widget_data = widget_data
        self._widget = widget_data._widget
        self._key_path = key_path
        self._original_data = original_data

    def clear(self):
        with self._widget.lock:
            self._original_data.clear()

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.CLEAR,
                payload=[
                    self._key_path,
                ],
            )

    def copy(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.copy(*args, **kwargs)

    def fromkeys(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.get(*args, **kwargs)

    def items(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.items()

    def keys(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.keys()

    def pop(self, key):
        with self._widget.lock:
            item = self._original_data.pop(key)

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.REMOVE,
                payload=[
                    self._key_path,
                    key,
                ],
            )

            return item

    def popitem(self):
        with self._widget.lock:
            key, value = self._original_data.popitem()

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.REMOVE,
                payload=[
                    self._key_path,
                    key,
                ],
            )

            return key, value

    def setdefault(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, update_dict):
        with self._widget.lock:
            for key, value in update_dict.items():
                self._original_data[key] = value

                self._widget.document.add_patch(
                    node_id=self._widget.id,
                    patch_type=PATCH_TYPE.WIDGET_DATA,
                    operation=OPERATION.SET,
                    payload=[
                        self._key_path,
                        key,
                        value,
                    ],
                )

    def values(self, *args, **kwargs):
        with self._widget.lock:
            return self._original_data.values()

    def __setitem__(self, name, item):
        with self._widget.lock:
            check_value(name)
            check_value(item)

            self._original_data[name] = item

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.SET,
                payload=[
                    self._key_path,
                    name,
                    item,
                ],
            )

    def __getitem__(self, name):
        with self._widget.lock:
            item = self._original_data[name]

            if isinstance(item, list):
                return ListOverlay(
                    widget_data=self._widget_data,
                    key_path=self._key_path + [name],
                    original_data=item,
                )

            if isinstance(item, dict):
                return DictOverlay(
                    widget_data=self._widget_data,
                    key_path=self._key_path + [name],
                    original_data=item,
                )

            return item

    def __delitem__(self, name):
        with self._widget.lock:
            del self._original_data[name]

            self._widget.document.add_patch(
                node_id=self._widget.id,
                patch_type=PATCH_TYPE.WIDGET_DATA,
                operation=OPERATION.REMOVE,
                payload=[
                    self._key_path,
                    name,
                ],
            )

    def __str__(self, *args, **kwargs):
        with self._widget.lock:
            return str(self._original_data)

    def __repr__(self, *args, **kwargs):
        with self._widget.lock:
            return repr(self._original_data)

    def __len__(self, *args, **kwargs):
        with self._widget.lock:
            return len(self._original_data)

    def __bool__(self, *args, **kwargs):
        with self._widget.lock:
            return bool(self._original_data)


class WidgetData:
    _LONA_CLASS_NAME = 'WidgetData'

    def __init__(self, widget):
        self._widget = widget

        self._reset({}, initial=True)

    def __getitem__(self, *args, **kwargs):
        return self._overlay.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self._overlay.__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self._overlay.__delitem__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        with self._widget.lock:
            return len(self._original_data)

    def __bool__(self, *args, **kwargs):
        with self._widget.lock:
            return bool(self._original_data)

    def __getattribute__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)

        if hasattr(self._overlay, name):
            return getattr(self._overlay, name)

        return super().__getattribute__(name)

    def __dir__(self):
        return [
            *super().__dir__(),
            *dir(self._overlay),
        ]

    # serialisation ###########################################################
    def _reset(self, value, initial=False):
        if not isinstance(value, (dict, list)):
            raise ValueError('widget state has to be dict or list')

        check_value(value)

        with self._widget.lock:
            self._data = value

            if not initial:
                self._widget.document.add_patch(
                    node_id=self._widget.id,
                    patch_type=PATCH_TYPE.WIDGET_DATA,
                    operation=OPERATION.RESET,
                    payload=[
                        [],
                        deepcopy(value)
                    ],
                )

            if isinstance(value, list):
                self._overlay = ListOverlay(
                    widget_data=self,
                    key_path=[],
                    original_data=self._data
                )

            elif isinstance(value, dict):
                self._overlay = DictOverlay(
                    widget_data=self,
                    key_path=[],
                    original_data=self._data
                )

    def _serialize(self):
        return deepcopy(self._data)

    # string representation ###################################################
    def __repr__(self):
        return '<WidgetData({}))>'.format(repr(self._data))
