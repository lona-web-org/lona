import pytest


@pytest.mark.dependency()
def test_attribute_dict():
    from lona.html import Div

    # init ####################################################################
    d = Div(foo='foo', bar='bar')

    assert d.attributes['foo'] == 'foo'
    assert d.attributes['bar'] == 'bar'

    # reset ###################################################################
    d = Div()

    d.attributes = {
        'foo': 'foo',
        'bar': 'bar',
    }

    assert d.attributes == {
        'foo': 'foo',
        'bar': 'bar',
    }

    # value errors ############################################################
    with pytest.raises(ValueError):
        d = Div(foo={})

    d = Div()

    with pytest.raises(RuntimeError):
        d.attributes['id'] = 'foo'

    # comparisons #############################################################
    d = Div()

    assert not bool(d.attributes)

    d.attributes['foo'] = 'foo'

    assert bool(d.attributes)
