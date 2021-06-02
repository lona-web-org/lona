import importlib
import inspect
import runpy


def acquire(import_string, ignore_import_cache=False):
    attribute = None

    # scripts
    if '::' in import_string:
        script, attribute_name = import_string.split('::')
        attributes = runpy.run_path(script, run_name=script)

        if attribute_name not in attributes:
            raise ImportError("script '{}' has no attribute '{}'".format(
                script, attribute_name))

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

    else:
        raise TypeError('invalid import string')

    return attribute


def get_file(obj):
    if obj.__module__.endswith('.py'):
        return obj.__module__

    return inspect.getfile(obj)


def get_object_repr(obj):
    return '<{} object at {}>'.format(
        obj.__class__.__name__,
        hex(id(obj)),
    )
