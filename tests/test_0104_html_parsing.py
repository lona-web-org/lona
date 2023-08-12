import pytest

from lona.html import (
    NumberInput,
    TextInput,
    TextArea,
    CheckBox,
    Select2,
    Option2,
    Submit,
    Select,
    Option,
    Button,
    HTML2,
    HTML1,
    Node,
    Div,
)
from lona.compat import set_use_future_node_classes


# HTML1 #######################################################################
def test_empty_node():
    node = HTML1('<div></div>')[0]

    assert node.tag_name == 'div'
    assert node.id_list == []
    assert node.class_list == []
    assert node.style == {}
    assert node.attributes == {}
    assert node.nodes == []


def test_node_with_attributes():
    node = HTML1("""
        <div id="foo" class="bar" style="color: black" foo="bar">
        </div>
    """)[0]

    assert node.tag_name == 'div'
    assert node.id_list == ['foo']
    assert node.class_list == ['bar']
    assert node.style == {'color': 'black'}
    assert node.attributes == {'foo': 'bar'}
    assert node.nodes == []


def test_sub_nodes():
    node = HTML1("""
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


def test_multiple_ids():
    node = HTML1('<div id="foo bar baz"></div>')[0]

    assert node.id_list == ['foo', 'bar', 'baz']


def test_multiple_classes():
    node = HTML1('<div class="foo bar baz"></div>')[0]

    assert node.class_list == ['foo', 'bar', 'baz']


def test_multiple_styles():
    node = HTML1('<div style="color: black; display: block"></div>')[0]

    assert node.style == {
        'color': 'black',
        'display': 'block',
    }


def test_multiple_attributes():
    node = HTML1('<div foo="bar" bar="baz"></div>')[0]

    assert node.attributes == {
        'foo': 'bar',
        'bar': 'baz',
    }


def test_high_level_nodes():
    node = HTML1('<button>Click me</button>')[0]

    assert type(node) is Button


def test_boolean_property_without_value():
    node = HTML1('<button disabled>Click me</button>')[0]

    assert node.disabled


def test_boolean_property_with_value():
    node = HTML1('<button disabled="true">Click me</button>')[0]

    assert node.disabled


def test_missing_end_tag():
    with pytest.raises(
            ValueError,
            match='Invalid html: missing end tag </span>',
    ):
        HTML1('<span>')


def test_wrong_end_tag():
    with pytest.raises(
            ValueError,
            match='Invalid html: </div> expected, </span> received',
    ):
        HTML1('<p><div>abc</span></p>')


def test_end_tag_without_start_tag():
    with pytest.raises(
            ValueError,
            match='Invalid html: missing start tag for </span>',
    ):
        HTML1('<div>abc</div></span>')


def test_missing_start_tag():
    with pytest.raises(
            ValueError,
            match='Invalid html: missing start tag for </span>',
    ):
        HTML1('</span>')


def test_self_closing_tag_with_slash():
    img = HTML1('<div><img src="abc"/></div>')[0].nodes[0]

    assert img.tag_name == 'img'
    assert img.self_closing_tag is True


def test_self_closing_tag_without_slash():
    img = HTML1('<div><img src="abc"></div>')[0].nodes[0]

    assert img.tag_name == 'img'
    assert img.self_closing_tag is True


def test_non_self_closing_tag():
    div = HTML1('<div></div>')[0]

    assert div.tag_name == 'div'
    assert div.self_closing_tag is False


def test_non_self_closing_tag_with_slash():
    span = HTML1('<div><span/></div>')[0].nodes[0]

    assert span.tag_name == 'span'
    assert span.self_closing_tag is True


def test_default_input_type_is_text():
    node = HTML1('<input value="abc"/>')[0]

    assert type(node) is TextInput
    assert node.value == 'abc'
    assert node.disabled is False


def test_input_type_text():
    node = HTML1('<input type="text" value="xyz" disabled/>')[0]

    assert type(node) is TextInput
    assert node.value == 'xyz'
    assert node.disabled is True


def test_input_type_unknown():
    node = HTML1('<input type="unknown"/>')[0]

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
        'reset',  # intentionally, see 575dcf635180 ("html: remove Reset node")  # NOQA: LN002
        'search',
        'tel',
        'time',
        'url',
        'week',
    ],
)
def test_not_implemented_input_types(tp):
    node = HTML1(f'<input type="{tp}"/>')[0]

    assert type(node) is Node


def test_input_type_number():
    node = HTML1('<input type="number" value="123.5"/>')[0]

    assert type(node) is NumberInput
    assert node.value == 123.5


def test_input_type_checkbox():
    node = HTML1('<input type="checkbox"/>')[0]

    assert type(node) is CheckBox
    assert node.value is False


def test_input_type_checkbox_checked():
    node = HTML1('<input type="checkbox" checked/>')[0]

    assert type(node) is CheckBox
    assert node.value is True


def test_input_type_submit():
    node = HTML1('<input type="submit"/>')[0]

    assert type(node) is Submit


def test_textarea():
    node = HTML1('<textarea>abc</textarea>')[0]

    assert type(node) is TextArea
    assert node.value == 'abc'


def test_textarea_with_self_closing_tag_inside():
    textarea = HTML1('<textarea>abc<br/>xyz</textarea>')[0]

    assert textarea.value == 'abc<br/>xyz'


def test_textarea_with_pair_tag_inside():
    textarea = HTML1('<textarea>aaa <b>bbb</b> ccc</textarea>')[0]

    assert textarea.value == 'aaa <b>bbb</b> ccc'


def test_select():
    node = HTML1("""
        <select>
            <option value="1">a</option>
            <option value="2" selected>b</option>
        </select>
    """)[0]

    assert type(node) is Select
    assert type(node.nodes[0]) is Option
    assert node.value == '2'


def test_select2():
    set_use_future_node_classes(True)

    try:
        node = HTML1("""
            <select>
                <option value="1">a</option>
                <option value="2" selected>b</option>
            </select>
        """)[0]

        assert type(node) is Select2
        assert type(node.nodes[0]) is Option2
        assert node.value == '2'

    finally:
        set_use_future_node_classes(False)


def test_attribute_escaping():
    node = Div(style='font-family: "Times New Roman"')

    assert node.style['font-family'] == '"Times New Roman"'
    assert node.style.to_sub_attribute_string() == 'font-family: &quot;Times New Roman&quot;'  # NOQA: E501

    node = HTML1(str(node))[0]

    assert node.style['font-family'] == '"Times New Roman"'


# HTML2 #######################################################################
def test_HTML2_sub_nodes():
    node = HTML2("""
        <div>
            <span></span>
            <div></div>
            <h1></h1>
        </div>
    """)

    assert not node.parent
    assert node.tag_name == 'div'
    assert len(node.nodes) == 3
    assert node.nodes[0].tag_name == 'span'
    assert node.nodes[1].tag_name == 'div'
    assert node.nodes[2].tag_name == 'h1'


def test_wrapping():
    node = HTML2("""
        <span></span>
        <div></div>
        <h1></h1>
    """)

    assert node.tag_name == 'div'
    assert len(node.nodes) == 3
    assert node.nodes[0].tag_name == 'span'
    assert node.nodes[1].tag_name == 'div'
    assert node.nodes[2].tag_name == 'h1'


def test_multiple_strings():
    node = HTML2(
        '<span></span><span></span>',
        '<div></div>',
        '<h1></h1>',
    )

    assert node.tag_name == 'div'
    assert len(node.nodes) == 4
    assert node.nodes[0].tag_name == 'span'
    assert node.nodes[1].tag_name == 'span'
    assert node.nodes[2].tag_name == 'div'
    assert node.nodes[3].tag_name == 'h1'


def test_attribute_cases():
    node1 = HTML1('<svg preserveAspectRatio="none"></svg>')[0]
    node2 = HTML2('<svg preserveAspectRatio="none"></svg>')

    assert node1.attributes['preserveAspectRatio'] == 'none'
    assert node2.attributes['preserveAspectRatio'] == 'none'
