import pytest

from lona.html import RadioButton, RadioGroup, Label, Div
from lona.html.text_node import TextNode


def test_values():

    # no value
    radio_group = RadioGroup(
        RadioButton(value='foo'),
        RadioButton(value='bar'),
        RadioButton(value='baz'),
    )

    assert radio_group.value is None
    assert radio_group.values == ('foo', 'bar', 'baz')
    assert radio_group.checked_radio_button is None
    assert len(radio_group.radio_buttons) == 3

    # pre set value
    radio_group = RadioGroup(
        RadioButton(value='foo', checked=True),
        RadioButton(value='bar'),
        RadioButton(value='baz'),
    )

    assert radio_group.value == 'foo'
    assert radio_group.values == ('foo', 'bar', 'baz')
    assert radio_group.checked_radio_button is radio_group[0]
    assert len(radio_group.radio_buttons) == 3

    # reset values
    radio_group = RadioGroup(
        RadioButton(value='foo'),
        RadioButton(value='bar'),
        RadioButton(value='baz'),
    )

    radio_group.value = 'foo'

    assert radio_group.value == 'foo'
    assert radio_group[0].checked
    assert not radio_group[1].checked
    assert not radio_group[2].checked

    # invalid value
    radio_group = RadioGroup(
        RadioButton(value='foo'),
        RadioButton(value='bar'),
        RadioButton(value='baz'),
    )

    with pytest.raises(ValueError, match=r'^no radio button with value'):
        radio_group.value = 'foobar'


def test_add_button():

    # string value pair
    radio_group = RadioGroup()

    radio_group.add_button('Foo', 10)

    assert len(radio_group.nodes) == 2
    assert isinstance(radio_group[0], Label)
    assert radio_group[0][0] == TextNode('Foo')
    assert isinstance(radio_group[1], RadioButton)
    assert radio_group[0].attributes['for'] in radio_group[1].id_list
    assert radio_group[1].value == 10

    # label and radio button
    radio_group = RadioGroup()

    radio_group.add_button(Label('Foo'), RadioButton(value=10))

    assert len(radio_group.nodes) == 2
    assert isinstance(radio_group[0], Label)
    assert radio_group[0][0] == TextNode('Foo')
    assert isinstance(radio_group[1], RadioButton)
    assert radio_group[0].attributes['for'] in radio_group[1].id_list
    assert radio_group[1].value == 10

    # nested nodes
    radio_group = RadioGroup()

    radio_group.add_button(Div(Label('Foo'), RadioButton(value=10)))

    assert len(radio_group.nodes) == 1
    assert len(radio_group.nodes[0]) == 2
    assert isinstance(radio_group[0][0], Label)
    assert radio_group[0][0][0] == TextNode('Foo')
    assert isinstance(radio_group[0][1], RadioButton)
    assert radio_group[0][0].attributes['for'] in radio_group[0][1].id_list
    assert radio_group[0][1].value == 10

    # radio button in label
    radio_group = RadioGroup()

    radio_group.add_button(Label('Foo', RadioButton(value=10)))

    assert len(radio_group.nodes) == 1
    assert isinstance(radio_group[0], Label)
    assert radio_group[0][0] == TextNode('Foo')
    assert isinstance(radio_group[0][1], RadioButton)
    assert radio_group[0].attributes['for'] in radio_group[0][1].id_list
    assert radio_group[0][1].value == 10
