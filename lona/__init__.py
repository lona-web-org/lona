# TODO: remove LonaView in 2.0

try:
    from .exceptions import *  # NOQA: F403
    from .routing import MATCH_ALL, Route
    from .errors import *  # NOQA: F403
    from .view import View as LonaView
    from .app import LonaApp
    from .view import View

except ImportError as e:  # pragma: no cover
    # this can happen while installing the package and can be ignored
    if e.name != 'typing_extensions':
        raise

VERSION = (1, 10, 5, 1)
VERSION_STRING = '.'.join(str(i) for i in VERSION)
