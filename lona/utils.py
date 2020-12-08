from types import ModuleType
import importlib
import inspect
import runpy


def acquire(import_string, ignore_import_cache=False):
    path = ''
    attribute = None

    # scripts
    if '::' in import_string:
        script, attribute_name = import_string.split('::')
        attributes = runpy.run_path(script)

        if attribute_name not in attributes:
            raise ImportError("script '{}' has no attribute '{}'".format(
                script, attribute_name))

        path = script
        attribute = attributes[attribute_name]

    # modules
    elif '.' in import_string:
        module_name, attribute_name = import_string.rsplit('.', 1)
        module = importlib.import_module(module_name)

        # ignore import cache
        if ignore_import_cache:
            path = inspect.getfile(module)

            return acquire('{}::{}'.format(path, attribute_name))

        if not hasattr(module, attribute_name):
            raise ImportError("module '{}' has no attribute '{}'".format(
                module_name, attribute_name))

        attribute = getattr(module, attribute_name)

        if isinstance(attribute, ModuleType):
            path = inspect.getfile(attribute)

        else:
            path = inspect.getfile(module)

    else:
        raise TypeError('invalid import string')

    return path, attribute


class Mapping:
    def __init__(self):
        self.entries = []

    def get_entry(self, key):
        for entry in self.entries:
            if entry[0] == key:
                return entry

    def keys(self):
        return [i[0] for i in self.entries]

    def items(self):
        for entry in self.entries:
            yield entry

    def __getitem__(self, key):
        entry = self.get_entry(key)

        if not entry:
            raise KeyError(key)

        return entry[1]

    def __setitem__(self, key, value):
        entry = self.get_entry(key)

        if entry:
            entry[1] = value

        else:
            self.entries.append([key, value])

    def __contains__(self, key):
        return bool(self.get_entry(key))

    def __repr__(self):
        d = {}

        for key, value in self.entries:
            d[repr(key)] = value

        return repr(d)
