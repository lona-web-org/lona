from lona.html import Tr, Td


def test_number_of_serialize_calls(mocker):

    from lona.html import Node

    spy = mocker.spy(Node, '_serialize')

    tr = Tr()
    for i in range(100):
        tr.append(Td(i))

    assert spy.call_count < 150
