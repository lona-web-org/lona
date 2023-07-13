from lona.html import Div


def test_state():
    div = Div()

    assert hasattr(div, 'state')
    assert hasattr(div.state, 'lock')

    assert div.state == {}

    div.state['foo'] = 'bar'

    assert div.state == {'foo': 'bar'}

    div.state.clear()

    assert div.state == {}


def test_initial_state():
    div = Div(state={'foo': 'bar'})

    assert div.state == {'foo': 'bar'}
