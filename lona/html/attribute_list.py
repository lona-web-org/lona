from time import monotonic_ns

from lona.protocol import OPERATION, PATCH_TYPE


class AttributeList:
    PATCH_TYPE = None

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = list(*args, **kwargs)
        self._changes = []

    # list helper #############################################################
    def add(self, attribute):
        if not isinstance(attribute, (int, bool, float, str)):
            raise ValueError('unsupported type')

        with self._node.document.lock:
            if attribute in self._attributes:
                return

            self._attributes.append(attribute)

            self._changes.append([
                monotonic_ns(),
                self._node._id,
                self.PATCH_TYPE,
                OPERATION.ADD,
                attribute,
            ])

    def remove(self, attribute):
        with self._node.document.lock:
            if attribute not in self._attributes:
                return

            self._attributes.remove(attribute)

            self._changes.append([
                monotonic_ns(),
                self._node._id,
                self.PATCH_TYPE,
                OPERATION.REMOVE,
                attribute,
            ])

    def clear(self):
        with self._node.document.lock:
            if not self._attributes:
                return

            self._attributes.clear()

            self._changes.append([
                monotonic_ns(),
                self._node._id,
                self.PATCH_TYPE,
                OPERATION.CLEAR,
            ])

    def toggle(self, attribute):
        with self._node.document.lock:
            if attribute in self._attributes:
                self.remove(attribute)

            else:
                self.add(attribute)

    def append(self, attribute):
        return self.add(attribute)

    def extend(self, attributes):
        with self._node.document.lock:
            for attribute in iter(attributes):
                if attribute in self._attributes:
                    continue

                self.append(attribute)

    def __len__(self):
        with self._node.document.lock:
            return len(self._attributes)

    def __bool__(self):
        with self._node.document.lock:
            return bool(self._attributes)

    def __iter__(self):
        with self._node.document.lock:
            return self._attributes.__iter__()

    # serialisation ###########################################################
    def _reset(self, value):
        if not isinstance(value, list):
            raise ValueError('unsupported type')

        for i in value:
            if not isinstance(i, (int, bool, float, str)):
                raise ValueError('unsupported type')

        with self._node.document.lock:
            self._attributes = value

            self._changes.append([
                monotonic_ns(),
                self._node._id,
                self.PATCH_TYPE,
                OPERATION.RESET,
                list(value),
            ])

    def _has_changes(self):
        return bool(self._changes)

    def _get_changes(self):
        return list(self._changes)

    def _clear_changes(self):
        return self._changes.clear()

    def _serialize(self):
        return list(self._attributes)

    # string representation ###################################################
    def __str__(self):
        with self._node.document.lock:
            return ' '.join([i for i in self._attributes])

    def __repr__(self):
        return '<AttributeList({})>'.format(repr(self._attributes))


class IDList(AttributeList):
    PATCH_TYPE = PATCH_TYPE.ID_LIST

    def __repr__(self):
        return '<IDList({})>'.format(repr(self._attributes))


class ClassList(AttributeList):
    PATCH_TYPE = PATCH_TYPE.CLASS_LIST

    def __repr__(self):
        return '<ClassList({})>'.format(repr(self._attributes))
