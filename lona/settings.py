from copy import deepcopy
import logging
import types
import runpy

logger = logging.getLogger('lona.settings')


class Settings:
    def __init__(self):
        self._paths = []
        self._values = {}

    def add(self, path):
        if not path.endswith('.py'):
            logger.error(
                "'%s' does not look like python script (modules are not supported)",  # NOQA
                path,
            )

            return

        self._paths.append(path)

        try:
            values = runpy.run_path(
                path,
                init_globals=self._values,
                run_name=path,
            )

        except Exception:
            logger.error(
                "exception raised while loading settings '%s'",
                path,
                exc_info=True
            )

            return

        self._values = {}

        for key, value in values.items():
            if key.startswith('_'):
                continue

            if isinstance(value, types.ModuleType):
                continue

            self._values[key] = deepcopy(value)

    def get(self, *args):
        return self._values.get(*args)

    def update(self, settings):
        self._values.update(settings)

    def __iter__(self):
        return self._values.__iter__()

    def __getattribute__(self, name):
        if name in ('get', 'add', 'update') or name.startswith('_'):
            return super().__getattribute__(name)

        return self._values[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)

        self._values[name] = value

    def __dir__(self):
        return [
            *super().__dir__(),
            *self._values.keys(),
        ]
