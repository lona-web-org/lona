import pytest

from lona.routing import Router, Route


class TestBasicRouting:
    def setup_method(self):
        self.routes = [
            Route('/foo/<arg>/', None),
            Route('/foo/', None),
            Route('/bar/<arg>/', None),
            Route('/', None),
        ]

        self.router = Router()
        self.router.add_routes(*self.routes)

    def test_resolve_without_arguments(self):
        match, route, match_info = self.router.resolve('/foo/')

        assert match
        assert route == self.routes[1]
        assert match_info == {}

    def test_resolve_with_argument(self):
        match, route, match_info = self.router.resolve('/foo/bar/')

        assert match
        assert route == self.routes[0]
        assert match_info == {'arg': 'bar'}

    def test_resolve_with_argument_2(self):
        match, route, match_info = self.router.resolve('/bar/foo/')

        assert match
        assert route == self.routes[2]
        assert match_info == {'arg': 'foo'}

    def test_resolve_root(self):
        match, route, match_info = self.router.resolve('/')

        assert match
        assert route == self.routes[3]
        assert match_info == {}

    def test_cant_resolve_unknown_route(self):
        match, route, match_info = self.router.resolve('/foobar/')

        assert not match


class TestRoutesWithRegex:
    def setup_method(self):
        self.routes = [
            Route('/number/<number:[0-9]+>/', None),
        ]

        self.router = Router()
        self.router.add_routes(*self.routes)

    def test_match_regex(self):
        match, route, match_info = self.router.resolve('/number/14/')

        assert match
        assert route == self.routes[0]
        assert match_info == {'number': '14'}

    def test_doesnt_match_regex(self):
        match, route, match_info = self.router.resolve('/number/14a/')

        assert not match


class TestOptionalTrailingSlash:
    def setup_method(self):
        self.routes = [
            Route('/foo(/)', None),
            Route('/bar/', None),
            Route('/foobar/<arg>(/)', None),
        ]

        self.router = Router()
        self.router.add_routes(*self.routes)

    def test_optional_slash_resolves_without_slash(self):
        match, route, match_info = self.router.resolve('/foo')

        assert match
        assert route == self.routes[0]
        assert match_info == {}

    def test_optional_slash_resolves_with_slash(self):
        match, route, match_info = self.router.resolve('/foo/')

        assert match
        assert route == self.routes[0]
        assert match_info == {}

    def test_optional_slash_resolves_without_slash_and_argument(self):
        match, route, match_info = self.router.resolve('/foobar/foobar')

        assert match
        assert route == self.routes[2]
        assert match_info == {'arg': 'foobar'}

    def test_optional_slash_resolves_with_slash_and_argument(self):
        match, route, match_info = self.router.resolve('/foobar/foobar/')

        assert match
        assert route == self.routes[2]
        assert match_info == {'arg': 'foobar'}

    def test_required_slash_doesnt_resolve_without_slash(self):
        match, route, match_info = self.router.resolve('/bar')

        assert not match

    def test_required_slash_resolves_with_slash(self):
        match, route, match_info = self.router.resolve('/bar/')

        assert match
        assert route == self.routes[1]
        assert match_info == {}


class TestReverseMatching:
    def setup_method(self):
        routes = [
            Route('/foo/<arg>/', None, name='foo'),
            Route('/bar/', None, name='bar'),
            Route('/foobar/<arg>(/)', None, name='foobar'),
        ]
        self.router = Router()
        self.router.add_routes(*routes)

    def test_reverse_with_arg(self):
        url = self.router.reverse('foo', arg='bar')

        assert url == '/foo/bar/'

    def test_reverse_with_arg_and_optional_slash(self):
        url = self.router.reverse('foobar', arg='foobar')

        assert url == '/foobar/foobar'

    def test_reverse_without_arg(self):
        url = self.router.reverse('bar')

        assert url == '/bar/'

    def test_reverse_unknown_arg(self):
        with pytest.raises(ValueError, match='missing URL arg: arg'):
            self.router.reverse('foo', foo='bar')

    def test_reverse_unknown_name(self):
        with pytest.raises(ValueError, match="no route named 'baz' found"):
            self.router.reverse('baz')
