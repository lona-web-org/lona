from lona.html import Widget, Span, Node, Div
from lona.html.text_node import TextNode


def test_simple_comparison():
    assert Div() == Div()
    assert Div() is not Div()
    assert Div() != Widget()
    assert Div() != TextNode('')


def test_text_nodes():
    assert TextNode('foo') == TextNode('foo')
    assert TextNode('foo') != TextNode('bar')
    assert TextNode('foo') is not TextNode('foo')


def test_legacy_widgets():
    # TODO: remove in 2.0

    class TestWidget(Widget):
        def __init__(self, *nodes, **widget_data):
            self.nodes = nodes
            self.data = widget_data

    assert TestWidget() == TestWidget()

    assert TestWidget(Div()) == TestWidget(Div())
    assert TestWidget(Div()) != TestWidget(Span())

    assert TestWidget(foo=1) == TestWidget(foo=1)
    assert TestWidget(foo=1) != TestWidget()
    assert TestWidget(foo=1) != TestWidget(foo=2)
    assert TestWidget(foo=1) != TestWidget(foo=1, bar=2)


def test_non_node_comparisons():
    assert Div() != 'Div'
    assert Div() != object()


def test_namespaces():
    assert Div() != Div(namespace='foo')
    assert Div(namespace='foo') != Div(namespace='bar')


def test_tag_name():
    assert Div() != Span()
    assert Node(tag_name='div') != Node(tag_name='span')


def test_id_list():
    assert Div(_id='foo') == Div(_id='foo')
    assert Div(_id='foo') != Div()
    assert Div(_id='foo') != Div(_id='foo bar')


def test_class_list():
    assert Div(_class='foo') == Div(_class='foo')
    assert Div(_class='foo') != Div()
    assert Div(_class='foo') != Div(_class='foo bar')


def test_style():
    assert Div(style={'color': 'red'}) == Div(style={'color': 'red'})
    assert Div(style={'color': 'red'}) != Div(style={'color': 'blue'})
    assert Div(style={'color': 'red'}) != Div(style={'color': 'red', 'a': 'b'})


def test_attributes():
    assert Div(a=1) == Div(a=1)
    assert Div(a=1) != Div(a=2)
    assert Div(a=1) != Div(a=1, b=2)


def test_sub_nodes():
    assert Div(Div()) == Div(Div())
    assert Div(Div()) != Div(Div(a=1))
    assert Div(Div()) != Div(Div(Span()))
    assert Div(Div()) != Div()


def test_widgets():
    assert Div(widget='foo') == Div(widget='foo')
    assert Div(widget='foo') != Div()


def test_widget_data():
    assert Div(widget_data=['foo']) == Div(widget_data=['foo'])
    assert Div(widget_data=['foo']) != Div(widget_data=['foo', 'bar'])
    assert Div(widget_data=['foo']) != Div()
