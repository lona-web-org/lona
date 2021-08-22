try:
    from .routing import Route, MATCH_ALL  # NOQA
    from .view import LonaView  # NOQA
    from .app import LonaApp  # NOQA
    from .exceptions import *  # NOQA
    from .errors import *  # NOQA

except ImportError:
    # this happens while packaging and can be ignored

    pass

VERSION = (1, 3)
VERSION_STRING = '{}'.format('.'.join([str(i) for i in VERSION]))
