# TODO: remove LonaView and LonaApp in 2.0

from .exceptions import *  # NOQA: F403
from .responses import *  # NOQA: F403
from .routing import MATCH_ALL, Route
from .errors import *  # NOQA: F403
from .view import View as LonaView
from .app import App as LonaApp
from .channels import Channel
from .request import Request
from .buckets import Bucket
from .view import View
from .app import App

VERSION = (1, 16, 1)
VERSION_STRING = '.'.join(str(i) for i in VERSION)
