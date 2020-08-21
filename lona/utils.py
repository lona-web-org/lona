from traceback import format_exception
from types import ModuleType
from textwrap import indent
from pprint import pformat
from html import escape
import importlib
import datetime
import inspect
import logging
import runpy


def pretty_print(*args, **kwargs):
    return escape(pformat(*args, **kwargs))


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


class Flag:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __bool__(self):
        return self.value

    def __eq__(self, other):
        return other == self.value

    def set(self, value):
        self.value = value


class LogFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.excluded = []
        self.included = []

    def format(self, record):
        if record.name in self.excluded:
            return ''

        if self.included and record.name not in self.included:
            return ''

        # format record string
        time_stamp = datetime.datetime.fromtimestamp(record.created)
        time_stamp_str = time_stamp.strftime('%H:%M:%S.%f')

        record_string = '{}{} {}{} {} {} {}'.format(
            record.threadName,
            (24 - len(record.threadName)) * ' ',

            record.levelname,
            (8 - len(record.levelname)) * ' ',

            time_stamp_str,
            record.name,
            record.getMessage(),
        )

        # format exc_info
        if record.exc_info:
            record_string = '{}\n{}'.format(
                record_string,
                indent(
                    ''.join(format_exception(*record.exc_info))[:-1],
                    prefix='  ',
                ),
            )

        # colors
        RED = '31'
        YELLOW = '33'
        WHITE = '37'
        GREEN = '32'
        BACKGROUND_RED = '41'

        BRIGHT = '1'

        if record.levelname == 'DEBUG':
            style = ''
            background = ''
            color = GREEN

        elif record.levelname == 'INFO':
            style = ''
            background = ''
            color = WHITE

        elif record.levelname == 'WARNING':
            style = ''
            background = ''
            color = YELLOW

        elif record.levelname == 'ERROR':
            style = BRIGHT
            background = ''
            color = RED

        elif record.levelname == 'CRITICAL':
            style = BRIGHT
            background = BACKGROUND_RED
            color = WHITE

        if style:
            color = ';{}'.format(color)

        if background and color:
            background = ';{}'.format(background)

        return '\033[{}{}{}m{}\033[00m'.format(
            style,
            color,
            background,
            record_string,
        )

    def include(self, logger_name):
        self.included.append(logger_name)

    def exclude(self, logger_name):
        self.excluded.append(logger_name)


def setup_log(log_level=logging.INFO):
    log = LogFormatter()

    logging.basicConfig(level=log_level)

    for handler in logging.getLogger().root.handlers:
        handler.setFormatter(log)

    return log
