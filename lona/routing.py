from functools import lru_cache
import logging
import re

from lona import default_settings

ABSTRACT_ROUTE_RE = re.compile(r'<(?P<name>[^:>]+)(:(?P<pattern>[^>]+))?>')
ROUTE_PART_FORMAT_STRING = r'(?P<{}>{})'
DEFAULT_PATTERN = r'[^/]+'
OPTIONAL_TRAILING_SLASH_PATTERN = r'(/)'

MATCH_ALL = 1

logger = logging.getLogger('lona.routing')


class Route:
    def __init__(self, raw_pattern, view, name='', interactive=True,
                 http_pass_through=False, frontend_view=None):

        self.raw_pattern = raw_pattern
        self.view = view
        self.name = name
        self.interactive = interactive
        self.http_pass_through = http_pass_through
        self.frontend_view = frontend_view

        self.path = None
        self.format_string = ''
        self.optional_trailing_slash = False

        # match all
        if self.raw_pattern == MATCH_ALL:
            self.path = MATCH_ALL

        # string or regex
        else:
            if self.raw_pattern.endswith(OPTIONAL_TRAILING_SLASH_PATTERN):
                self.optional_trailing_slash = True

            groups = ABSTRACT_ROUTE_RE.findall(self.raw_pattern)

            # path is no pattern but simple string
            if not groups:
                self.path = self.raw_pattern
                self.format_string = self.raw_pattern

                if self.optional_trailing_slash:
                    suffix_len = len(OPTIONAL_TRAILING_SLASH_PATTERN) * -1

                    self.path = self.path[:suffix_len]
                    self.format_string = self.path[:suffix_len]

                return

            pattern_names = [i[0] for i in groups]
            patterns = [(i[0], i[2] or DEFAULT_PATTERN, ) for i in groups]
            cleaned_pattern = ABSTRACT_ROUTE_RE.sub('{}', self.raw_pattern)

            # setup format string
            self.format_string = cleaned_pattern.format(
                *['{' + i + '}' for i in pattern_names])

            # compile pattern
            self.pattern = re.compile(
                r'^{}{}$'.format(
                    cleaned_pattern.format(
                        *[ROUTE_PART_FORMAT_STRING.format(*i)
                          for i in patterns]
                    ),
                    (OPTIONAL_TRAILING_SLASH_PATTERN
                        if self.optional_trailing_slash else ''),
                )
            )

    def match(self, path):
        # match all
        if self.path == MATCH_ALL:
            return True, {}

        # simple string
        if self.path:
            if self.optional_trailing_slash and path.endswith('/'):
                path = path[:-1]

            return path == self.path, {}

        # pattern
        match_object = self.pattern.match(path)

        if not match_object:
            return False, {}

        return True, match_object.groupdict()

    def __repr__(self):
        raw_pattern = self.raw_pattern

        if raw_pattern == MATCH_ALL:
            raw_pattern = 'MATCH_ALL'

        return '<Route({}, {})>'.format(
            raw_pattern,
            self.view,
        )


class Router:
    def __init__(self):
        self.routes = []

        self.resize_resolve_cache(
            default_settings.ROUTING_RESOLVE_CACHE_MAX_SIZE,
        )

        self.resize_reverse_cache(
            default_settings.ROUTING_REVERSE_CACHE_MAX_SIZE,
        )

    # caches ##################################################################
    def resize_resolve_cache(self, max_size):
        self._resolve_lru_cache = lru_cache(max_size)(self._resolve)

    def resize_reverse_cache(self, max_size):
        self._reverse_lru_cache = lru_cache(max_size)(self._reverse)

    def get_resolve_cache_info(self):
        return self._resolve_lru_cache.cache_info()

    def get_reverse_cache_info(self):
        return self._reverse_lru_cache.cache_info()

    def clear_resolve_cache_info(self):
        return self._resolve_lru_cache.cache_clear()

    def clear_reverse_cache_info(self):
        return self._reverse_lru_cache.cache_clear()

    # routes ##################################################################
    def add_route(self, route):
        self.routes.append(route)

    def add_routes(self, *routes):
        for route in routes:
            self.add_route(route)

    # resolve #################################################################
    def _resolve(self, path):
        logger.debug("resolving '%s'", path)

        for route in self.routes:
            match, match_info = route.match(path)

            if match:
                logger.debug('%s matched', route)

                return True, route, match_info

        logger.debug("no match for '%s'", path)

        return False, None, {}

    def resolve(self, *args, **kwargs):
        return self._resolve_lru_cache(*args, **kwargs)

    # reverse #################################################################
    def _reverse(self, name, *args, **kwargs):
        route = None

        for i in self.routes:
            if i.name == name:
                route = i

                break

        if not route:
            raise ValueError("no route named '{}' found".format(name))

        if route.path:
            return route.path

        key_error = None

        try:
            return route.format_string.format(*args, **kwargs)

        except KeyError as e:
            key_error = e

        raise ValueError('missing URL arg: {} '.format(key_error.args[0]))

    def reverse(self, *args, **kwargs):
        return self._reverse_lru_cache(*args, **kwargs)
