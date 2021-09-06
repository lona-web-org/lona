try:
    from .routing import Route, MATCH_ALL
    from .view import LonaView
    from .app import LonaApp
    from .exceptions import *  # NOQA: F403
    from .errors import *  # NOQA: F403

except ImportError:
    # this happens while packaging and can be ignored

    pass

VERSION = (1, 6)
VERSION_STRING = '.'.join(str(i) for i in VERSION)
