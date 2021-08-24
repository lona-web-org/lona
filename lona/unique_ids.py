from threading import Lock


class UniqueIDGenerator:
    def __init__(self):
        self._lock = Lock()
        self._value = 0

    def __call__(self):
        with self._lock:
            self._value += 1

            return str(self._value)


_name_spaces = {
    '': UniqueIDGenerator(),
    'nodes': UniqueIDGenerator(),
    'view_runtimes': UniqueIDGenerator(),
}


def generate_unique_id(name_space=''):
    return _name_spaces[name_space]()
