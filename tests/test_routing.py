import pytest


def test_basic_routing():
    from lona.routing import Router, Route

    router = Router()

    routes = [
        Route('/foo/<arg>/', None),
        Route('/foo/', None),
        Route('/bar/<arg>/', None),
        Route('/', None),
    ]

    router.add_routes(*routes)

    # /foo/
    match, route, match_info = router.resolve('/foo/')

    assert match
    assert route == routes[1]
    assert match_info == {}

    # /foo/bar/
    match, route, match_info = router.resolve('/foo/bar/')

    assert match
    assert route == routes[0]
    assert match_info == {'arg': 'bar'}

    # /bar/foo/
    match, route, match_info = router.resolve('/bar/foo/')

    assert match
    assert route == routes[2]
    assert match_info == {'arg': 'foo'}

    # /
    match, route, match_info = router.resolve('/')

    assert match
    assert route == routes[3]
    assert match_info == {}

    # /foobar/
    match, route, match_info = router.resolve('/foobar/')

    assert not match


def test_routes_with_regexes():
    from lona.routing import Router, Route

    router = Router()

    routes = [
        Route('/number/<number:[0-9]+>/', None),
    ]

    router.add_routes(*routes)

    # /number/14/
    match, route, match_info = router.resolve('/number/14/')

    assert match
    assert route == routes[0]
    assert match_info == {'number': '14'}

    # /number/14a/
    match, route, match_info = router.resolve('/number/14a/')

    assert not match


def test_optional_trailing_slash():
    from lona.routing import Router, Route

    router = Router()

    routes = [
        Route('/foo(/)', None),
        Route('/bar/', None),
    ]

    router.add_routes(*routes)

    # /foo
    match, route, match_info = router.resolve('/foo')

    assert match
    assert route == routes[0]
    assert match_info == {}

    # /foo/
    match, route, match_info = router.resolve('/foo/')

    assert match
    assert route == routes[0]
    assert match_info == {}

    # /bar
    match, route, match_info = router.resolve('/bar')

    assert not match

    # /bar/
    match, route, match_info = router.resolve('/bar/')

    assert match
    assert route == routes[1]
    assert match_info == {}


def test_reverse_matching():
    from lona.routing import Router, Route

    router = Router()

    routes = [
        Route('/foo/<arg>/', None, name='foo'),
        Route('/bar/', None, name='bar'),
    ]

    router.add_routes(*routes)

    # /foo/bar/
    url = router.reverse('foo', arg='bar')

    assert url == '/foo/bar/'

    # /bar/
    url = router.reverse('bar')

    assert url == '/bar/'

    # /foo/bar/ but wrongly named arg
    with pytest.raises(ValueError, match='missing URL arg: arg'):
        url = router.reverse('foo', foo='bar')

    # unknown name
    with pytest.raises(ValueError, match="no route named 'baz' found"):
        url = router.reverse('baz')
