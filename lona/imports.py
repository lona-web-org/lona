from __future__ import annotations

import importlib
import inspect
import runpy


def acquire(import_string, ignore_import_cache=False):
    # script attribute
    if '::' in import_string:
        script, attribute_name = import_string.split('::')
        attributes = runpy.run_path(script, run_name=script)

        if attribute_name not in attributes:
            raise ImportError(
                f"script '{script}' has no attribute '{attribute_name}'",
            )

        return attributes[attribute_name]

    # module attribute
    elif '.' in import_string:
        module_name, attribute_name = import_string.rsplit('.', 1)
        module = importlib.import_module(module_name)

        # ignore import cache
        if ignore_import_cache:
            path = inspect.getfile(module)

            return acquire(f'{path}::{attribute_name}')

        if not hasattr(module, attribute_name):
            raise ImportError(
                f"module '{module_name}' has no attribute '{attribute_name}'",
            )

        return getattr(module, attribute_name)

    # module
    return importlib.import_module(import_string)


def get_file(obj):
    if obj.__module__.endswith('.py'):
        return obj.__module__

    return inspect.getfile(obj)


def get_object_repr(obj):
    return f'<{obj.__class__.__name__} object at {hex(id(obj))}>'
