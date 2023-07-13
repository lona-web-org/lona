import pytest

from lona.html import Div


def test_default_id_list_is_empty():
    d = Div()

    assert d.id_list == []


def test_initial_id_can_be_list():
    d = Div(_id=['foo', 'bar'])

    assert d.id_list == ['foo', 'bar']


def test_initial_id_can_be_space_separated_str():
    d = Div(_id='foo bar')

    assert d.id_list == ['foo', 'bar']


def test_initial_id_can_be_passed_via_kwargs():
    d = Div(**{'id': 'foo bar'})

    assert d.id_list == ['foo', 'bar']


def test_default_class_list_is_empty():
    d = Div()

    assert d.class_list == []


def test_initial_class_can_be_list():
    d = Div(_class=['foo', 'bar'])

    assert d.class_list == ['foo', 'bar']


def test_initial_class_can_be_space_separated_str():
    d = Div(_class='foo bar')

    assert d.class_list == ['foo', 'bar']


def test_initial_class_can_be_passed_via_kwargs():
    d = Div(**{'class': 'foo bar'})

    assert d.class_list == ['foo', 'bar']


def test_set_id_list():
    d = Div()

    d.id_list = ['foo', 'bar']

    assert d.id_list == ['foo', 'bar']


def test_set_class_list():
    d = Div()

    d.class_list = ['foo', 'bar']

    assert d.class_list == ['foo', 'bar']


def test_initial_id_cant_be_dict():
    with pytest.raises(
            ValueError,
            match='id has to be string or list of strings',
    ):
        Div(_id={})


def test_cant_set_dict():
    d = Div()

    with pytest.raises(
            ValueError,
            match="unsupported type: <class 'dict'>",
    ):
        d.id_list = {}


def test_cant_set_list_with_dict():
    d = Div()

    with pytest.raises(
            ValueError,
            match="unsupported type: <class 'dict'>",
    ):
        d.id_list = [{}]


def test_default_list_has_zero_len():
    d = Div()

    assert len(d.id_list) == 0


def test_len_returns_number_of_elements():
    d = Div(_id='foo bar')

    assert len(d.id_list) == 2


def test_non_equality():
    d = Div(_id='foo bar')

    assert d.id_list != []
    assert d.id_list != ['foo', 'bar', 'baz']


def test_equality_ignores_order():
    d = Div(_id='foo bar')

    assert d.id_list == ['bar', 'foo']


def test_equality_ignored_duplicates():
    d = Div(_id='foo bar')

    assert d.id_list == ['foo', 'bar', 'foo', 'bar']


def test_in_keyword():
    d = Div(_id='foo bar')

    assert 'foo' in d.id_list
    assert 'bar' in d.id_list
    assert 'baz' not in d.id_list


def test_non_empty_list_is_true():
    d = Div(_id='foo')

    assert bool(d.id_list)


def test_empty_list_is_false():
    d = Div()

    assert not bool(d.id_list)


def test_add_one_element():
    d = Div()

    d.id_list.add('foo')

    assert d.id_list == ['foo']


def test_add_existing_element_does_nothing():
    d = Div()
    d.id_list.add('foo')

    d.id_list.add('foo')

    assert d.id_list == ['foo']


def test_cant_add_dict():
    d = Div()

    with pytest.raises(
            ValueError,
            match="unsupported type: <class 'dict'>",
    ):
        d.id_list.add({})


def test_extend():
    d = Div(_id='foo')

    d.id_list.extend(['bar', 'baz'])

    assert d.id_list == ['foo', 'bar', 'baz']


def test_extend_ignores_duplicates():
    d = Div(_id='foo')

    d.id_list.extend(['foo', 'bar', 'baz'])

    assert d.id_list == ['foo', 'bar', 'baz']


def test_remove_existing_element():
    d = Div(_id='foo bar')

    d.id_list.remove('foo')

    assert d.id_list == ['bar']


def test_remove_unknown_element():
    d = Div(_id='bar')

    d.id_list.remove('foo')

    assert d.id_list == ['bar']


def test_clear():
    d = Div(_id='foo bar')

    d.id_list.clear()

    assert d.id_list == []


def test_clear_empty_list():
    d = Div()

    d.id_list.clear()

    assert d.id_list == []


def test_toggle_existing_element():
    d = Div(_id='foo bar')

    d.id_list.toggle('foo')

    assert d.id_list == ['bar']


def test_toggle_unknown_element():
    d = Div(_id='bar')

    d.id_list.toggle('foo')

    assert d.id_list == ['foo', 'bar']
