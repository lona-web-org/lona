from copy import copy

ATTRIBUTE_NAME = 'data-lona-events'


class NodeEventList:
    def __init__(self, node, event_types):
        self._node = node
        self._event_types = copy(event_types)

        self._apply()

    def __repr__(self):
        return '<NodeEventList({})>'.format(self._event_types)

    @property
    def lock(self):
        return self._node.lock

    def _get_index(self, event_type):
        for index, _event_type in enumerate(self._event_types):
            if _event_type == event_type:
                return index

        return -1

    def _apply(self):
        with self.lock:
            attribute_string = []

            for event_type in self._event_types:
                attribute_string.append(event_type.serialize())

            attribute_string = ';'.join(attribute_string)

            if attribute_string:
                self._node.attributes[ATTRIBUTE_NAME] = attribute_string

            elif ATTRIBUTE_NAME in self._node.attributes:
                del self._node.attributes[ATTRIBUTE_NAME]

    def _reset(self, value):
        with self.lock:
            self._event_types = value
            self._apply()

    def add(self, event_type):
        with self.lock:
            index = self._get_index(event_type)

            if index > -1:
                self._event_types.pop(index)

            self._event_types.append(event_type)
            self._apply()

    def remove(self, event_type):
        with self.lock:
            index = self._get_index(event_type)

            if index == -1:
                return

            self._event_types.remove(event_type)
            self._apply()

    def clear(self):
        with self.lock:
            if not self._event_types:
                return

            self._event_types.clear()
            self._apply()

    def append(self, *args, **kwargs):
        return self.add(*args, **kwargs)

    def extend(self, event_types):
        with self.lock:
            for event_type in event_types:
                if event_type in self._event_types:
                    continue

                self._event_types.append(event_type)

            self._apply()

    def toggle(self, event_type):
        with self.lock:
            if event_type in self._event_types:
                self._event_types.remove(event_type)

            else:
                self._event_types.append(event_type)

            self._apply()
