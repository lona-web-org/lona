from threading import RLock


class Overlay:
    def __init__(self, server_state, data):
        self._server_state = server_state
        self._data = data

    @property
    def lock(self):
        return self._server_state.lock

    def __getattribute__(self, name):
        if name.startswith('_') or name == 'lock':
            return super().__getattribute__(name)

        attribute = self._data.__getattribute__(name)

        def shim(*args, **kwargs):
            with self.lock:
                return attribute(*args, **kwargs)

        if callable(attribute):
            return shim

        return attribute

    def __getitem__(self, key):
        with self.lock:
            item = self._data.__getitem__(key)

            if isinstance(item, (dict, list, Overlay)):
                return Overlay(self._server_state, item)

            return item

    def __setitem__(self, key, value):
        with self.lock:
            self._data.__setitem__(key, value)

    def __iter__(self):
        with self.lock:
            return self._data.__iter__()

    def __bool__(self):
        with self.lock:
            return self._data.__bool__()

    def __dir__(self):
        with self.lock:
            return self._data.__dir__()

    def __len__(self):
        with self.lock:
            return self._data.__len__()

    def __str__(self):
        with self.lock:
            return self._data.__str__()

    def __repr__(self):
        with self.lock:
            return self._data.__repr__()


class ServerState(Overlay):
    def __init__(self, initial_data=None):
        self._server_state = self
        self._data = initial_data or {}
        self._lock = RLock()

    @property
    def lock(self):
        return self._lock
