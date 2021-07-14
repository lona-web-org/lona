from lona.protocol import OPERATION, PATCH_TYPE


class AttributeList:
    PATCH_TYPE = None

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = list(*args, **kwargs)

    # list helper #############################################################
    def add(self, attribute):
        if not isinstance(attribute, (int, bool, float, str)):
            raise ValueError('unsupported type: {}'.format(type(attribute)))

        with self._node.lock:
            if attribute in self._attributes:
                return

            self._attributes.append(attribute)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.ADD,
                payload=[
                    attribute,
                ],
            )

    def remove(self, attribute):
        with self._node.lock:
            if attribute not in self._attributes:
                return

            self._attributes.remove(attribute)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.REMOVE,
                payload=[
                    attribute,
                ],
            )

    def clear(self):
        with self._node.lock:
            if not self._attributes:
                return

            self._attributes.clear()

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.CLEAR,
                payload=[],
            )

    def toggle(self, attribute):
        with self._node.lock:
            if attribute in self._attributes:
                self.remove(attribute)

            else:
                self.add(attribute)

    def append(self, attribute):
        return self.add(attribute)

    def extend(self, attributes):
        with self._node.lock:
            for attribute in iter(attributes):
                if attribute in self._attributes:
                    continue

                self.append(attribute)

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._attributes

            elif not isinstance(other, (list, set, tuple)):
                return False

            other = set(other)
            common_attributes = set(self._attributes) & other

            return (len(self._attributes) == len(other) and
                    len(self._attributes) == len(common_attributes))

    def __len__(self):
        with self._node.lock:
            return len(self._attributes)

    def __bool__(self):
        with self._node.lock:
            return bool(self._attributes)

    def __iter__(self):
        with self._node.lock:
            return self._attributes.__iter__()

    # serialisation ###########################################################
    def _reset(self, value):
        if not isinstance(value, list):
            raise ValueError('unsupported type: {}'.format(type(value)))

        for i in value:
            if not isinstance(i, (int, bool, float, str)):
                raise ValueError('unsupported type: {}'.format(type(value)))

        with self._node.lock:
            self._attributes = value

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.RESET,
                payload=[
                    list(value),
                ],
            )

    def _serialize(self):
        return list(self._attributes)

    # string representation ###################################################
    def __str__(self):
        with self._node.lock:
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
