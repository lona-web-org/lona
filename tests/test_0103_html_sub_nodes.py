import pytest

from lona.html import Div


def test_nodes_in_nodes():
    div1 = Div()

    div2 = Div(
        div1,
    )

    assert len(div2) == 1
    assert div2[0] is div1


def test_text_nodes_in_nodes():
    div = Div('foo')

    assert len(div) == 1
    assert str(div[0]) == 'foo'


def test_mixed_nodes():
    sub_node1 = Div()
    sub_node2 = Div()

    div = Div(
        sub_node1,
        'foo',
        sub_node2,
        'bar',
    )

    assert len(div) == 4
    assert div[0] is sub_node1
    assert str(div[1]) == 'foo'
    assert div[2] is sub_node2
    assert str(div[3]) == 'bar'


def test_generator():
    div = Div(
        (Div() for i in range(10)),
    )

    assert len(div) == 10


def test_list():
    div = Div(
        [Div() for i in range(10)],
    )

    assert len(div) == 10


def test_slices():
    div1 = Div()
    div2 = Div()
    div3 = Div()
    div4 = Div()
    outer_div = Div(div1, div2, div3, div4)
    outer_div.nodes = outer_div[1:-1]

    assert div1 not in outer_div
    assert div2 in outer_div
    assert div3 in outer_div
    assert div4 not in outer_div


def test_node_uniqueness():
    """
    Nodes are unique and may be mounted in only one node tree, at only one
    location. To ensure this, unmounts nodes at their parent, if they have
    a parent, before mounting them.
    """

    # multiple mounts of the same node
    # the resulting node should have only one child
    outer_div = Div()
    inner_div = Div()

    outer_div.append(inner_div)
    outer_div.append(inner_div)
    outer_div.append(inner_div)

    assert inner_div in outer_div
    assert len(outer_div) == 1

    # unmounting
    # the given node is already mounted somewhere else in the tree, so it
    # has to be unmounted before mounting it somewhere else
    inner_div = Div()

    outer_div = Div(
        Div(),
        Div(inner_div),
    )

    outer_div[0].append(inner_div)

    assert inner_div in outer_div[0]
    assert inner_div not in outer_div[1]


def test_node_loop_detection():

    # simple loop
    div = Div(Div())

    with pytest.raises(RuntimeError, match='loop detected'):
        div[0].append(div)

    # multi node loop
    div = Div(Div(Div(Div())))

    with pytest.raises(RuntimeError, match='loop detected'):
        div[0][0][0].append(div[0][0])


def test_sub_node_reset_with_node():
    div1 = Div()
    div2 = Div()

    div1.nodes = div2

    assert len(div1.nodes) == 1
    assert div1.nodes[0] is div2


def test_sub_node_reset_with_node_list():
    div1 = Div()
    div2 = Div()

    div1.nodes = [div2]

    assert len(div1.nodes) == 1
    assert div1.nodes[0] is div2
