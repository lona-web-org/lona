import logging
import re

from lona.types import Symbol

ABSTRACT_ROUTE_RE = re.compile(r'<(?P<name>[^:>]+)(:(?P<pattern>[^>]+))?>')
ROUTE_PART_FORMAT_STRING = r'(?P<{}>{})'
DEFAULT_PATTERN = r'[^/]+'
OPTIONAL_TRAILING_SLASH_PATTERN = r'(/)?'

MATCH_ALL = Symbol('MATCH_ALL', 1)

logger = logging.getLogger('lona.routing')


class Route:
    def __init__(self, *args, name='', method='*', interactive=True,
                 http_pass_through=False, frontend_view=None):

        self.method = '*'
        self.raw_pattern = ''
        self.format_string = ''
        self.view = None
        self.name = name
        self.optional_trailing_slash = False
        self.interactive = interactive
        self.http_pass_through = http_pass_through
        self.frontend_view = frontend_view

        if len(args) == 3:
            self.method, self.raw_pattern, self.view = args

        elif len(args) == 2:
            self.raw_pattern, self.view = args

        else:
            raise ValueError('to few arguments')

        if method:
            self.method = method

        # parse raw path
        self.path = None

        # match all
        if self.raw_pattern == MATCH_ALL:
            self.path = MATCH_ALL

        # string or regex
        else:
            if self.raw_pattern.endswith('(/)'):
                self.optional_trailing_slash = True

            groups = ABSTRACT_ROUTE_RE.findall(self.raw_pattern)

            # path is no pattern but simple string
            if not groups:
                self.path = self.raw_pattern
                self.format_string = self.raw_pattern

                if self.optional_trailing_slash:
                    self.path = self.path[:-3]

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
        return '<Route({}, {}, {})>'.format(
            self.method,
            self.raw_pattern,
            self.view,
        )


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, route):
        self.routes.append(route)

    def add_routes(self, *routes):
        for route in routes:
            self.add_route(route)

    def resolve(self, path):
        logger.debug("resolving '%s'", path)

        for route in self.routes:
            match, match_info = route.match(path)

            if match:
                logger.debug('%s matched', route)

                return True, route, match_info

        logger.debug("no match for '%s'", path)

        return False, None, {}

    def reverse(self, name, *args, **kwargs):
        route = None

        for i in self.routes:
            if i.name == name:
                route = i

                break

        if not route:
            raise ValueError("no route named '{}' found".format(name))

        if route.path:
            return route.path

        return route.format_string.format(*args, **kwargs)
