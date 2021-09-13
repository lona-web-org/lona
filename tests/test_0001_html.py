import re

import pytest


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
    with pytest.raises(ValueError, match="unsupported type: <class 'dict'>"):
        d = Div(foo={})

    d = Div()

    with pytest.raises(
            RuntimeError,
            match=re.escape(
                "Node.attributes['id'] is not supported. "
                'Use Node.id_list instead.',
            ),
    ):
        d.attributes['id'] = 'foo'

    # comparisons #############################################################
    d = Div()

    assert not bool(d.attributes)

    d.attributes['foo'] = 'foo'

    assert bool(d.attributes)


def test_attribute_dict_pop():
    from lona.html import Div

    d = Div(foo='foo-val', bar='bar-val')

    assert 'foo' in d.attributes
    assert d.attributes.pop('foo') == 'foo-val'
    assert 'foo' not in d.attributes

    assert 'xxx' not in d.attributes
    with pytest.raises(KeyError, match='xxx'):
        d.attributes.pop('xxx')
    assert 'xxx' not in d.attributes

    assert d.attributes.pop('xxx', 'yyy') == 'yyy'
    assert 'xxx' not in d.attributes

    assert 'bar' in d.attributes
    assert d.attributes.pop('bar', 'yyy') == 'bar-val'
    assert 'bar' not in d.attributes

    with pytest.raises(
            TypeError,
            match='pop expected at most 2 arguments, got 3'
    ):
        d.attributes.pop('xxx', 'yyy', 'zzz')


def test_attribute_dict_del():
    from lona.html import Div

    d = Div(foo='foo-val', bar='bar-val')

    assert 'foo' in d.attributes
    del d.attributes['foo']
    assert 'foo' not in d.attributes

    assert 'xxx' not in d.attributes
    del d.attributes['xxx']
    assert 'xxx' not in d.attributes


def test_attribute_list():
    from lona.html import Div

    # init ####################################################################
    # id
    d = Div()

    assert d.id_list == []

    d = Div(_id=['foo', 'bar'])

    assert d.id_list == ['foo', 'bar']

    d = Div(_id='foo bar')

    assert d.id_list == ['foo', 'bar']

    d = Div(**{'id': 'foo bar'})

    assert d.id_list == ['foo', 'bar']

    # class
    d = Div()

    assert d.class_list == []

    d = Div(_class=['foo', 'bar'])

    assert d.class_list == ['foo', 'bar']

    d = Div(_class='foo bar')

    assert d.class_list == ['foo', 'bar']

    d = Div(**{'class': 'foo bar'})

    assert d.class_list == ['foo', 'bar']

    # reset ###################################################################
    # id
    d = Div()

    d.id_list = ['foo', 'bar']

    assert d.id_list == ['foo', 'bar']

    # class
    d = Div()

    d.class_list = ['foo', 'bar']

    assert d.class_list == ['foo', 'bar']

    # value errors ############################################################
    with pytest.raises(
            ValueError,
            match='id has to be string or list of strings',
    ):
        d = Div(_id={})

    with pytest.raises(ValueError, match="unsupported type: <class 'dict'>"):
        d.id_list = {}

    with pytest.raises(ValueError, match="unsupported type: <class 'list'>"):
        d.id_list = [{}]

    # len #####################################################################
    d = Div()

    assert len(d.id_list) == 0

    d = Div(_id='foo bar')

    assert len(d.id_list) == 2

    # comparisons #############################################################
    d = Div(_id='foo bar')

    assert d.id_list != []
    assert d.id_list != ['foo', 'bar', 'baz']
    assert d.id_list == ['foo', 'bar']
    assert d.id_list == ['bar', 'foo']
    assert d.id_list == ['foo', 'bar', 'foo', 'bar']

    assert 'foo' in d.id_list
    assert 'bar' in d.id_list
    assert 'baz' not in d.id_list

    d = Div(_id='foo')

    assert bool(d.id_list)

    d = Div()

    assert not bool(d.id_list)

    # add #####################################################################
    d = Div()

    d.id_list.add('foo')

    assert d.id_list == ['foo']

    d = Div()

    d.id_list.add('foo')
    d.id_list.add('foo')

    assert d.id_list == ['foo']

    d = Div()

    with pytest.raises(ValueError, match="unsupported type: <class 'dict'>"):
        d.id_list.add({})

    # extend ##################################################################
    d = Div(_id='foo')

    d.id_list.extend(['bar', 'baz'])

    assert d.id_list == ['foo', 'bar', 'baz']

    d = Div(_id='foo')

    d.id_list.extend(['foo', 'bar', 'baz'])

    assert d.id_list == ['foo', 'bar', 'baz']

    # remove ##################################################################
    d = Div(_id='foo bar')

    d.id_list.remove('foo')

    assert d.id_list == ['bar']

    d.id_list.remove('foo')

    assert d.id_list == ['bar']

    # clear ###################################################################
    d = Div(_id='foo bar')

    d.id_list.clear()

    assert d.id_list == []

    d = Div()

    d.id_list.clear()

    assert d.id_list == []

    # toggle ##################################################################
    d = Div(_id='foo bar')

    d.id_list.toggle('foo')

    assert d.id_list == ['bar']

    d.id_list.toggle('foo')

    assert d.id_list == ['foo', 'bar']


def test_html_strings():
    from lona.html import (
        NumberInput,
        TextInput,
        CheckBox,
        TextArea,
        Button,
        Select,
        Submit,
        HTML,
        Node,
    )

    # empty node ##############################################################
    node = HTML('<div></div>')[0]

    assert node.tag_name == 'div'
    assert node.id_list == []
    assert node.class_list == []
    assert node.style == {}
    assert node.attributes == {}
    assert node.nodes == []

    # node with attributes ####################################################
    node = HTML("""
        <div id="foo" class="bar" style="color: black" foo="bar">
        </div>
    """)[0]

    assert node.tag_name == 'div'
    assert node.id_list == ['foo']
    assert node.class_list == ['bar']
    assert node.style == {'color': 'black'}
    assert node.attributes == {'foo': 'bar'}
    assert node.nodes == []

    # sub nodes ###############################################################
    node = HTML("""
        <div>
            <span></span>
            <div></div>
            <h1></h1>
        </div>
    """)[0]

    assert node.tag_name == 'div'
    assert len(node.nodes) == 3
    assert node.nodes[0].tag_name == 'span'
    assert node.nodes[1].tag_name == 'div'
    assert node.nodes[2].tag_name == 'h1'

    # multiple ids ############################################################
    node = HTML('<div id="foo bar baz"></div>')[0]

    assert node.id_list == ['foo', 'bar', 'baz']

    # multiple classes ########################################################
    node = HTML('<div class="foo bar baz"></div>')[0]

    assert node.class_list == ['foo', 'bar', 'baz']

    # multiple css rules ######################################################
    node = HTML('<div style="color: black; display: block"></div>')[0]

    assert node.style == {
        'color': 'black',
        'display': 'block',
    }

    # multiple attributes #####################################################
    node = HTML('<div foo="bar" bar="baz"></div>')[0]

    assert node.attributes == {
        'foo': 'bar',
        'bar': 'baz',
    }

    # high level nodes ########################################################
    node = HTML('<button>Click me</button>')[0]

    assert type(node) is Button

    # boolean properties ######################################################
    node = HTML('<button disabled>Click me</button>')[0]

    assert node.disabled

    node = HTML('<button disabled="true">Click me</button>')[0]

    assert node.disabled

    # data binding nodes ######################################################
    node = HTML('<input value="abc"/>')[0]  # default type is text

    assert type(node) is TextInput
    assert node.value == 'abc'
    assert node.disabled is False

    node = HTML('<input type="text" value="xyz" disabled/>')[0]

    assert type(node) is TextInput
    assert node.value == 'xyz'
    assert node.disabled is True

    node = HTML('<input type="unknown"/>')[0]

    assert type(node) is Node

    not_implemented_types = [
        'button',
        'color',
        'date',
        'datetime-local',
        'email',
        'file',
        'hidden',
        'image',
        'month',
        'password',
        'radio',
        'range',
        'reset',  # intentionally, see 575dcf635180 ("html: remove Reset node")
        'search',
        'tel',
        'time',
        'url',
        'week',
    ]

    for tp in not_implemented_types:
        assert type(HTML(f'<input type="{tp}"/>')[0]) is Node

    node = HTML('<input type="number" value="123"/>')[0]

    assert type(node) is NumberInput
    assert node.value == 123

    node = HTML('<input type="checkbox"/>')[0]

    assert type(node) is CheckBox
    assert node.value is False

    node = HTML('<input type="checkbox" checked/>')[0]

    assert type(node) is CheckBox
    assert node.value is True

    node = HTML('<input type="submit"/>')[0]

    assert type(node) is Submit

    node = HTML('<textarea>abc</textarea>')[0]

    assert type(node) is TextArea
    assert node.value == ''
    # assert node.value == 'abc'  # TODO: fix in the next PR

    node = HTML("""
        <select>
            <option value="1">a</option>
            <option value="2" selected>b</option>
        </select>
    """)[0]

    assert type(node) == Select
    assert node.value == '2'


def test_number_input():
    from lona.html import NumberInput, HTML

    # default properties ######################################################

    node = NumberInput()

    assert node.value is None
    assert node.min is None
    assert node.max is None
    assert node.step == 1
    assert type(node.step) is int

    # default value type is int ###############################################

    node = NumberInput(value=123)

    assert node.value == 123
    assert type(node.value) is int

    # initial float step means float value type ###############################

    node = NumberInput(value=123, step=0.1)

    assert node.value == 123
    assert type(node.value) is float
    assert node.step == 0.1

    # initial int step means int value type ###################################

    node = NumberInput(value=123, step=3)

    assert node.value == 123
    assert type(node.value) is int

    # new float step changes value type to float ##############################

    node = NumberInput(value=123)
    node.step = 0.1

    assert node.value == 123
    assert type(node.value) is float

    # new int step changes value type to int ##################################

    node = NumberInput(value=123, step=0.1)
    node.step = 3

    assert node.value == 123
    assert type(node.value) is int

    # initial float value is not acceptable with default step #################

    with pytest.raises(TypeError, match='value should be None or int'):
        NumberInput(value=123.5)

    # float value is not acceptable with default step #########################

    node = NumberInput()

    with pytest.raises(TypeError, match='value should be None or int'):
        node.value = 123.5

    # parsing without step and int value ######################################

    node = HTML('<input type="number" value="123"/>')[0]

    assert node.value == 123
    assert type(node.value) is int
    assert node.min is None
    assert node.max is None
    assert node.step == 1

    # parsing without step and float value ####################################

    node = HTML('<input type="number" value="123.8"/>')[0]

    assert node.value == 123
    assert type(node.value) is int
    assert node.step == 1

    # parsing with broken step ####################################

    node = HTML('<input type="number" value="123" step="abc"/>')[0]

    assert node.value == 123
    assert type(node.value) is int
    assert node.step == 1

    # parsing with int step ###################################################

    node = HTML('<input type="number" value="123" step="3"/>')[0]

    assert node.value == 123
    assert type(node.value) is int
    assert node.step == 3
    assert type(node.step) is int

    # parsing with float step #################################################

    node = HTML('<input type="number" value="123" step="0.1"/>')[0]

    assert node.value == 123
    assert type(node.value) is float
    assert node.step == 0.1
    assert type(node.step) is float

    # parsing with float step and value #######################################

    node = HTML('<input type="number" value="123.8" step="0.1"/>')[0]

    assert node.value == 123.8
    assert type(node.value) is float
    assert node.step == 0.1
    assert type(node.step) is float

    # parsing broken value #######################################

    node = HTML('<input type="number" value="abc" step="0.1"/>')[0]

    assert node.value is None
