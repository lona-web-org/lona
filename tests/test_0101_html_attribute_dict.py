import re

import pytest

from lona.html import Div


def test_get_initial_values():
    d = Div(foo='foo', bar='bar')

    assert d.attributes['foo'] == 'foo'
    assert d.attributes['bar'] == 'bar'


def test_set_attributes():
    d = Div()

    d.attributes = {
        'foo': 'foo',
        'bar': 'bar',
    }

    assert d.attributes == {
        'foo': 'foo',
        'bar': 'bar',
    }


def test_value_cant_be_dict():
    with pytest.raises(
            ValueError,
            match="unsupported type: <class 'dict'>",
    ):
        Div(foo={})


def test_cant_use_id_key():
    d = Div()

    with pytest.raises(
            RuntimeError,
            match=re.escape(
                "Node.attributes['id'] is not supported. "
                'Use Node.id_list instead.',
            ),
    ):
        d.attributes['id'] = 'foo'


def test_empty_dict_is_false():
    d = Div()

    assert not bool(d.attributes)


def test_non_empty_dict_is_true():
    d = Div(foo='foo')

    assert bool(d.attributes)


def test_pop_existing_key():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'foo' in d.attributes

    val = d.attributes.pop('foo')

    assert val == 'foo-val'
    assert 'foo' not in d.attributes


def test_pop_unknown_key():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'xxx' not in d.attributes

    with pytest.raises(KeyError, match='xxx'):
        d.attributes.pop('xxx')
    assert 'xxx' not in d.attributes


def test_pop_unknown_key_with_default():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'xxx' not in d.attributes

    val = d.attributes.pop('xxx', 'yyy')

    assert val == 'yyy'
    assert 'xxx' not in d.attributes


def test_pop_existing_key_with_default():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'bar' in d.attributes

    val = d.attributes.pop('bar', 'yyy')

    assert val == 'bar-val'
    assert 'bar' not in d.attributes


def test_pop_expects_at_most_2_arguments():
    d = Div(foo='foo-val', bar='bar-val')

    with pytest.raises(
            TypeError,
            match='pop expected at most 2 arguments, got 3',
    ):
        d.attributes.pop('xxx', 'yyy', 'zzz')


def test_del_existing_key():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'foo' in d.attributes

    del d.attributes['foo']

    assert 'foo' not in d.attributes


def test_del_unknown_key():
    d = Div(foo='foo-val', bar='bar-val')
    assert 'xxx' not in d.attributes

    del d.attributes['xxx']

    assert 'xxx' not in d.attributes
