import re

import pytest

from lona.html import (
    NumberInput,
    TextInput,
    TextArea,
    CheckBox,
    Submit,
    Select,
    Button,
    Node,
    HTML,
    Div,
)


@pytest.mark.incremental()
class TestAttributeDict:
    def test_get_initial_values(self):
        d = Div(foo='foo', bar='bar')

        assert d.attributes['foo'] == 'foo'
        assert d.attributes['bar'] == 'bar'

    def test_set_attributes(self):
        d = Div()

        d.attributes = {
            'foo': 'foo',
            'bar': 'bar',
        }

        assert d.attributes == {
            'foo': 'foo',
            'bar': 'bar',
        }

    def test_value_cant_be_dict(self):
        with pytest.raises(
                ValueError,
                match="unsupported type: <class 'dict'>",
        ):
            Div(foo={})

    def test_cant_use_id_key(self):
        d = Div()

        with pytest.raises(
                RuntimeError,
                match=re.escape(
                    "Node.attributes['id'] is not supported. "
                    'Use Node.id_list instead.',
                ),
        ):
            d.attributes['id'] = 'foo'

    def test_empty_dict_is_false(self):
        d = Div()

        assert not bool(d.attributes)

    def test_non_empty_dict_is_true(self):
        d = Div(foo='foo')

        assert bool(d.attributes)

    def test_pop_existing_key(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'foo' in d.attributes

        val = d.attributes.pop('foo')

        assert val == 'foo-val'
        assert 'foo' not in d.attributes

    def test_pop_unknown_key(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'xxx' not in d.attributes

        with pytest.raises(KeyError, match='xxx'):
            d.attributes.pop('xxx')
        assert 'xxx' not in d.attributes

    def test_pop_unknown_key_with_default(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'xxx' not in d.attributes

        val = d.attributes.pop('xxx', 'yyy')

        assert val == 'yyy'
        assert 'xxx' not in d.attributes

    def test_pop_existing_key_with_default(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'bar' in d.attributes

        val = d.attributes.pop('bar', 'yyy')

        assert val == 'bar-val'
        assert 'bar' not in d.attributes

    def test_pop_expects_at_most_2_arguments(self):
        d = Div(foo='foo-val', bar='bar-val')

        with pytest.raises(
                TypeError,
                match='pop expected at most 2 arguments, got 3',
        ):
            d.attributes.pop('xxx', 'yyy', 'zzz')

    def test_del_existing_key(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'foo' in d.attributes

        del d.attributes['foo']

        assert 'foo' not in d.attributes

    def test_del_unknown_key(self):
        d = Div(foo='foo-val', bar='bar-val')
        assert 'xxx' not in d.attributes

        del d.attributes['xxx']

        assert 'xxx' not in d.attributes


@pytest.mark.incremental()
class TestAttributeList:
    def test_default_id_list_is_empty(self):
        d = Div()

        assert d.id_list == []

    def test_initial_id_can_be_list(self):
        d = Div(_id=['foo', 'bar'])

        assert d.id_list == ['foo', 'bar']

    def test_initial_id_can_be_space_separated_str(self):
        d = Div(_id='foo bar')

        assert d.id_list == ['foo', 'bar']

    def test_initial_id_can_be_passed_via_kwargs(self):
        d = Div(**{'id': 'foo bar'})

        assert d.id_list == ['foo', 'bar']

    def test_default_class_list_is_empty(self):
        d = Div()

        assert d.class_list == []

    def test_initial_class_can_be_list(self):
        d = Div(_class=['foo', 'bar'])

        assert d.class_list == ['foo', 'bar']

    def test_initial_class_can_be_space_separated_str(self):
        d = Div(_class='foo bar')

        assert d.class_list == ['foo', 'bar']

    def test_initial_class_can_be_passed_via_kwargs(self):
        d = Div(**{'class': 'foo bar'})

        assert d.class_list == ['foo', 'bar']

    def test_set_id_list(self):
        d = Div()

        d.id_list = ['foo', 'bar']

        assert d.id_list == ['foo', 'bar']

    def test_set_class_list(self):
        d = Div()

        d.class_list = ['foo', 'bar']

        assert d.class_list == ['foo', 'bar']

    def test_initial_id_cant_be_dict(self):
        with pytest.raises(
                ValueError,
                match='id has to be string or list of strings',
        ):
            Div(_id={})

    def test_cant_set_dict(self):
        d = Div()

        with pytest.raises(
                ValueError,
                match="unsupported type: <class 'dict'>",
        ):
            d.id_list = {}

    def test_cant_set_list_with_dict(self):
        d = Div()

        with pytest.raises(
                ValueError,
                match="unsupported type: <class 'dict'>",
        ):
            d.id_list = [{}]

    def test_default_list_has_zero_len(self):
        d = Div()

        assert len(d.id_list) == 0

    def test_len_returns_number_of_elements(self):
        d = Div(_id='foo bar')

        assert len(d.id_list) == 2

    def test_non_equality(self):
        d = Div(_id='foo bar')

        assert d.id_list != []
        assert d.id_list != ['foo', 'bar', 'baz']

    def test_equality_ignores_order(self):
        d = Div(_id='foo bar')

        assert d.id_list == ['bar', 'foo']

    def test_equality_ignored_duplicates(self):
        d = Div(_id='foo bar')

        assert d.id_list == ['foo', 'bar', 'foo', 'bar']

    def test_in_keyword(self):
        d = Div(_id='foo bar')

        assert 'foo' in d.id_list
        assert 'bar' in d.id_list
        assert 'baz' not in d.id_list

    def test_non_empty_list_is_true(self):
        d = Div(_id='foo')

        assert bool(d.id_list)

    def test_empty_list_is_false(self):
        d = Div()

        assert not bool(d.id_list)

    def test_add_one_element(self):
        d = Div()

        d.id_list.add('foo')

        assert d.id_list == ['foo']

    def test_add_existing_element_does_nothing(self):
        d = Div()
        d.id_list.add('foo')

        d.id_list.add('foo')

        assert d.id_list == ['foo']

    def test_cant_add_dict(self):
        d = Div()

        with pytest.raises(
                ValueError,
                match="unsupported type: <class 'dict'>",
        ):
            d.id_list.add({})

    def test_extend(self):
        d = Div(_id='foo')

        d.id_list.extend(['bar', 'baz'])

        assert d.id_list == ['foo', 'bar', 'baz']

    def test_extend_ignores_duplicates(self):
        d = Div(_id='foo')

        d.id_list.extend(['foo', 'bar', 'baz'])

        assert d.id_list == ['foo', 'bar', 'baz']

    def test_remove_existing_element(self):
        d = Div(_id='foo bar')

        d.id_list.remove('foo')

        assert d.id_list == ['bar']

    def test_remove_unknown_element(self):
        d = Div(_id='bar')

        d.id_list.remove('foo')

        assert d.id_list == ['bar']

    def test_clear(self):
        d = Div(_id='foo bar')

        d.id_list.clear()

        assert d.id_list == []

    def test_clear_empty_list(self):
        d = Div()

        d.id_list.clear()

        assert d.id_list == []

    def test_toggle_existing_element(self):
        d = Div(_id='foo bar')

        d.id_list.toggle('foo')

        assert d.id_list == ['bar']

    def test_toggle_unknown_element(self):
        d = Div(_id='bar')

        d.id_list.toggle('foo')

        assert d.id_list == ['foo', 'bar']


@pytest.mark.incremental()
class TestHTMLFromStr:
    def test_empty_node(self):
        node = HTML('<div></div>')[0]

        assert node.tag_name == 'div'
        assert node.id_list == []
        assert node.class_list == []
        assert node.style == {}
        assert node.attributes == {}
        assert node.nodes == []

    def test_node_with_attributes(self):
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

    def test_sub_nodes(self):
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

    def test_multiple_ids(self):
        node = HTML('<div id="foo bar baz"></div>')[0]

        assert node.id_list == ['foo', 'bar', 'baz']

    def test_multiple_classes(self):
        node = HTML('<div class="foo bar baz"></div>')[0]

        assert node.class_list == ['foo', 'bar', 'baz']

    def test_multiple_styles(self):
        node = HTML('<div style="color: black; display: block"></div>')[0]

        assert node.style == {
            'color': 'black',
            'display': 'block',
        }

    def test_multiple_attributes(self):
        node = HTML('<div foo="bar" bar="baz"></div>')[0]

        assert node.attributes == {
            'foo': 'bar',
            'bar': 'baz',
        }

    def test_high_level_nodes(self):
        node = HTML('<button>Click me</button>')[0]

        assert type(node) is Button

    def test_boolean_property_without_value(self):
        node = HTML('<button disabled>Click me</button>')[0]

        assert node.disabled

    def test_boolean_property_with_value(self):
        node = HTML('<button disabled="true">Click me</button>')[0]

        assert node.disabled

    def test_missing_end_tag(self):
        with pytest.raises(
                ValueError,
                match='Invalid html: missing end tag </span>',
        ):
            HTML('<span>')

    def test_wrong_end_tag(self):
        with pytest.raises(
                ValueError,
                match='Invalid html: </div> expected, </span> received',
        ):
            HTML('<p><div>abc</span></p>')

    def test_end_tag_without_start_tag(self):
        with pytest.raises(
                ValueError,
                match='Invalid html: missing start tag for </span>',
        ):
            HTML('<div>abc</div></span>')

    def test_missing_start_tag(self):
        with pytest.raises(
                ValueError,
                match='Invalid html: missing start tag for </span>',
        ):
            HTML('</span>')

    def test_default_input_type_is_text(self):
        node = HTML('<input value="abc"/>')[0]

        assert type(node) is TextInput
        assert node.value == 'abc'
        assert node.disabled is False

    def test_input_type_text(self):
        node = HTML('<input type="text" value="xyz" disabled/>')[0]

        assert type(node) is TextInput
        assert node.value == 'xyz'
        assert node.disabled is True

    def test_input_type_unknown(self):
        node = HTML('<input type="unknown"/>')[0]

        assert type(node) is Node

    @pytest.mark.parametrize(
        'tp',
        [
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
            'reset',  # intentionally, see 575dcf635180 ("html: remove Reset node")  # NOQA: E501
            'search',
            'tel',
            'time',
            'url',
            'week',
        ],
    )
    def test_not_implemented_input_types(self, tp):
        node = HTML(f'<input type="{tp}"/>')[0]

        assert type(node) is Node

    def test_input_type_number(self):
        node = HTML('<input type="number" value="123.5"/>')[0]

        assert type(node) is NumberInput
        assert node.value == 123.5

    def test_input_type_checkbox(self):
        node = HTML('<input type="checkbox"/>')[0]

        assert type(node) is CheckBox
        assert node.value is False

    def test_input_type_checkbox_checked(self):
        node = HTML('<input type="checkbox" checked/>')[0]

        assert type(node) is CheckBox
        assert node.value is True

    def test_input_type_submit(self):
        node = HTML('<input type="submit"/>')[0]

        assert type(node) is Submit

    def test_textarea(self):
        node = HTML('<textarea>abc</textarea>')[0]

        assert type(node) is TextArea
        assert node.value == 'abc'

    def test_textarea_with_self_closing_tag_inside(self):
        textarea = HTML('<textarea>abc<br/>xyz</textarea>')[0]

        assert textarea.value == 'abc<br/>xyz'

    def test_textarea_with_pair_tag_inside(self):
        textarea = HTML('<textarea>aaa <b>bbb</b> ccc</textarea>')[0]

        assert textarea.value == 'aaa <b>bbb</b> ccc'

    def test_select(self):
        node = HTML("""
            <select>
                <option value="1">a</option>
                <option value="2" selected>b</option>
            </select>
        """)[0]

        assert type(node) == Select
        assert node.value == '2'


@pytest.mark.incremental()
class TestNumberInput:
    def test_default_properties(self):
        node = NumberInput()

        assert node.value is None
        assert node.min is None
        assert node.max is None
        assert node.step is None

    def test_initial_value(self):
        node = NumberInput(value=12.3)

        assert node.value == 12.3

    def test_change_value(self):
        node = NumberInput()
        node.value = 12.3

        assert node.value == 12.3

    def test_parsing_no_attributes(self):
        node = HTML('<input type="number"/>')[0]

        assert node.value is None
        assert node.min is None
        assert node.max is None
        assert node.step is None

    def test_parsing_int_value(self):
        node = HTML('<input type="number" value="123"/>')[0]

        assert node.value == 123

    def test_parsing_float_value(self):
        node = HTML('<input type="number" value="12.3"/>')[0]

        assert node.value == 12.3

    def test_parsing_broken_step(self):
        node = HTML('<input type="number" value="123" step="abc"/>')[0]

        assert node.value == 123
        assert node.step is None

    def test_parsing_int_step(self):
        node = HTML('<input type="number" value="12.3" step="3"/>')[0]

        assert node.value == 12.3
        assert node.step == 3

    def test_parsing_float_step(self):
        node = HTML('<input type="number" value="12.3" step="0.1"/>')[0]

        assert node.value == 12.3
        assert node.step == 0.1

    def test_parsing_broken_value(self):
        node = HTML('<input type="number" value="abc" step="0.1"/>')[0]

        assert node.value is None

    def test_parsing_all_attributes(self):
        node = HTML(
            '<input type="number" value="12.3" min="15.3" max="20.5" step="0.2"/>',  # NOQA: E501
        )[0]

        assert node.value == 12.3
        assert node.min == 15.3
        assert node.max == 20.5
        assert node.step == 0.2
