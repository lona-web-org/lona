import pytest

from lona.html import HTML1, Span, Div, H1


def test_unsupported_selector():
    with pytest.raises(ValueError, match='unsupported selector feature:*'):
        HTML1().query_selector('div > div')


def test_query_selector():
    # test selectors by tag name
    html = Div(
        HTML1(),
        'foo',
        Div(
            H1(),
        ),
        Span(),
        Div(),
    )

    assert html.query_selector('h1') is html[2][0]
    assert html.query_selector('span') is html[3]

    # test selectors by id
    html = Div(
        HTML1(),
        'foo',
        Div(
            Div(_id='foo'),
            Div(_id='bar'),
        ),
        Div(_id='baz'),
    )

    assert html.query_selector('#foo') is html[2][0]
    assert html.query_selector('#baz') is html[3]

    # test selectors by class
    html = Div(
        HTML1(),
        'foo',
        Div(
            Div(_class='foo'),
            Div(_class='bar'),
        ),
        Div(_class='baz'),
    )

    assert html.query_selector('.foo') is html[2][0]
    assert html.query_selector('.baz') is html[3]

    # test selectors by attribute
    html = Div(
        HTML1(),
        'foo',
        Div(
            Div(_type='foo'),
            Div(_type='bar'),
        ),
        Div(_type='baz'),
    )

    assert html.query_selector('[type=foo]') is html[2][0]
    assert html.query_selector('[type=baz]') is html[3]


def test_query_selector_all():
    html = Div(
        Span(),
        Div(
            Span(),
        ),
        Span(),
    )

    nodes = html.query_selector_all('span')

    assert len(nodes) == 3
    assert html[0] in nodes
    assert html[1][0] in nodes
    assert html[2] in nodes


def test_closest():
    html = Div(
        Div(
            Div(
                Span(),
            ),
            _id='foo',
        ),
    )

    span = html[0][0][0]
    node = span.closest('div#foo')

    assert node is html[0]
