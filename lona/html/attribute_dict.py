from lona.protocol import OPERATION, PATCH_TYPE


class AttributeDict:
    PATCH_TYPE = PATCH_TYPE.ATTRIBUTES

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = dict(*args, **kwargs)

    # dict helper #############################################################
    def keys(self):
        with self._node.lock:
            return self._attributes.keys()

    def items(self):
        with self._node.lock:
            return self._attributes.items()

    def pop(self, name):
        with self._node.lock:
            if name not in self._attributes:
                return None

            attribute = self._attributes.pop(name)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.REMOVE,
                payload=[
                    name,
                ],
            )

            return attribute

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

    def get(self, *args, **kwargs):
        with self._node.lock:
            return self._attributes.get(*args, **kwargs)

    def update(self, value):
        if not isinstance(value, dict):
            raise ValueError('dict required')

        with self._node.lock:
            for key, value in value.items():
                self[key] = value

    def __getitem__(self, name):
        with self._node.lock:
            return self._attributes[name]

    def __setitem__(self, name, value, issuer=None):
        if not isinstance(value, (int, bool, float, str)):
            raise ValueError('unsupported type: {}'.format(type(value)))

        if name in ('id', 'class', 'style'):
            raise RuntimeError(
                "Node.attributes['{}'] is not supported. "
                'Use Node.{}{} instead.'.format(
                    name, name, '_list' if name != 'style' else '')
            )

        with self._node.lock:
            if name in self._attributes and self._attributes[name] == value:
                return

            self._attributes[name] = value

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.SET,
                payload=[
                    name,
                    value,
                ],
                issuer=issuer,
            )

    def __delitem__(self, name):
        self.pop(name)

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._attributes

        return self._attributes == other

    def __iter__(self):
        with self._node.lock:
            return self._attributes.__iter__()

    def __bool__(self):
        with self._node.lock:
            return bool(self._attributes)

    # serialisation ###########################################################
    def _reset(self, value):
        if not isinstance(value, dict):
            raise ValueError('unsupported type')

        for k, v in value.items():
            if not isinstance(v, (int, bool, float, str)):
                raise ValueError('unsupported type')

            if k in ('id', 'class', 'style'):
                raise RuntimeError(
                    "Node.attributes['{}'] is not supported. "
                    'Use Node.{}{} instead.'.format(
                        k, k, 'list' if k != 'style' else '')
                )

        with self._node.lock:
            self._attributes = value

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.RESET,
                payload=[
                    dict(value),
                ],
            )

    def _serialize(self):
        return dict(self._attributes)

    # string representation ###################################################
    def to_attribute_string(self, skip_value=False):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                if skip_value and key == 'value':
                    continue

                string.append('{}="{}"'.format(key, value))

            return ' '.join(string)

    def to_sub_attribute_string(self):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                string.append('{}: {}'.format(key, value))

            return '; '.join(string)

    def __repr__(self):
        return '<AttributeDict({})>'.format(repr(self._attributes))


class StyleDict(AttributeDict):
    PATCH_TYPE = PATCH_TYPE.STYLE

    def __init__(self, node, *args, **kwargs):
        args = list(args)

        for index, arg in enumerate(args):
            if isinstance(arg, str):
                args[index] = self._parse_style_string(arg)

        super().__init__(node, *args, **kwargs)

    def __repr__(self):
        return '<StyleDict({})>'.format(repr(self._attributes))

    def _parse_style_string(self, style_string):
        values = {}

        for css_rule in style_string.split(';'):
            if not css_rule.strip():
                continue

            if ':' not in css_rule:
                raise ValueError(
                    'Invalid style string: {}'.format(style_string)
                )

            name, value = css_rule.split(':', 1)

            values[name.strip()] = value.strip()

        return values

    def _reset(self, value):
        if isinstance(value, str):
            value = self._parse_style_string(value)

        return super()._reset(value)

    def update(self, value):
        if not isinstance(value, (dict, str)):
            raise ValueError('dict or string required')

        if isinstance(value, str):
            value = self._parse_style_string(value)

        return super().update(value)
