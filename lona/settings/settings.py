from copy import deepcopy
import importlib
import types
import runpy


class Settings:
    def add(self, import_string):
        # scripts
        if import_string.endswith('.py'):
            attributes = runpy.run_path(import_string)

            for name, value in attributes.items():
                if name.startswith('_') or name in ('add', 'get'):
                    continue

                if isinstance(value, types.ModuleType):
                    continue

                setattr(self, name, deepcopy(value))

        # modules
        else:
            module = importlib.import_module(import_string)

            for name in dir(module):
                if name.startswith('_') or name in ('add', 'get'):
                    continue

                value = getattr(module, name)

                if isinstance(value, types.ModuleType):
                    continue

                setattr(self, name, deepcopy(value))

    def get(self, *args):
        return getattr(self, *args)

    def __iter__(self):
        ignore = ('add', )

        for key in dir(self):
            if key in ignore or key.startswith('_'):
                continue

            yield key, getattr(self, key)
