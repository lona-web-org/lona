from dataclasses import dataclass
from enum import Enum


class SORT_ORDER(Enum):
    FRAMEWORK = 100
    LIBRARY = 200
    APPLICATION = 300


@dataclass
class StaticFile:
    name: str
    path: str
    url: str = ''
    sort_order: SORT_ORDER = SORT_ORDER.APPLICATION
    link: bool = True
    enabled_by_default: bool = True

    # this is only for internal use
    enabled: bool = True
    # this is only for the object representation and is meant for debugging
    static_url_prefix: str = ''


class StyleSheet(StaticFile):
    pass


class Script(StaticFile):
    pass
