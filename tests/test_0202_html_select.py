def test_select():
    import pytest

    from lona.html import Select, Option

    # basic API ###############################################################
    select = Select(
        values=[
            ('foo', 'Foo'),
            ('bar', 'Bar'),
            ('baz', 'Baz'),
        ],
    )

    assert not select.multiple

    # options
    assert len(select.nodes) == 3

    for option in select.nodes:
        assert type(option) is Option
        assert 'selected' not in option.attributes

    # values
    assert select.value == 'foo'

    assert select.values == [
        ('foo', 'Foo', False),
        ('bar', 'Bar', False),
        ('baz', 'Baz', False),
    ]

    select.value = 'bar'

    assert select.value == 'bar'

    assert select.values == [
        ('foo', 'Foo', False),
        ('bar', 'Bar', True),
        ('baz', 'Baz', False),
    ]

    assert 'selected' not in select.nodes[0].attributes
    assert 'selected' in select.nodes[1].attributes
    assert 'selected' not in select.nodes[0].attributes

    # disabled
    assert 'disabled' not in select.attributes

    select.disabled = True

    assert select.disabled
    assert 'disabled' in select.attributes

    select.disabled = False

    assert not select.disabled
    assert 'disabled' not in select.attributes

    with pytest.raises(TypeError):
        select.disabled = 'foo'

    # readonly
    assert 'readonly' not in select.attributes

    select.readonly = True

    assert select.readonly
    assert 'readonly' in select.attributes

    select.readonly = False

    assert not select.readonly
    assert 'readonly' not in select.attributes

    with pytest.raises(TypeError):
        select.readonly = 'foo'

    # multiple
    assert 'multiple' not in select.attributes

    select.multiple = True

    assert select.multiple
    assert 'multiple' in select.attributes

    select.multiple = False

    assert not select.multiple
    assert 'multiple' not in select.attributes

    with pytest.raises(TypeError):
        select.multiple = 'foo'

    # pre selected value ######################################################
    select = Select(
        values=[
            ('foo', 'Foo'),
            ('bar', 'Bar', True),
            ('baz', 'Baz'),
        ],
    )

    assert select.value == 'bar'

    assert select.values == [
        ('foo', 'Foo', False),
        ('bar', 'Bar', True),
        ('baz', 'Baz', False),
    ]

    # multi select ############################################################
    select = Select(
        values=[
            ('foo', 'Foo'),
            ('bar', 'Bar'),
            ('baz', 'Baz'),
        ],
        multiple=True,
    )

    assert select.values == [
        ('foo', 'Foo', False),
        ('bar', 'Bar', False),
        ('baz', 'Baz', False),
    ]

    assert select.value == []

    select.value = ['foo', 'bar']

    assert select.value == ['foo', 'bar']

    assert select.values == [
        ('foo', 'Foo', True),
        ('bar', 'Bar', True),
        ('baz', 'Baz', False),
    ]

    # multi select: pre selected values #######################################
    select = Select(
        values=[
            ('foo', 'Foo', True),
            ('bar', 'Bar', True),
            ('baz', 'Baz'),
        ],
        multiple=True,
    )

    assert select.values == [
        ('foo', 'Foo', True),
        ('bar', 'Bar', True),
        ('baz', 'Baz', False),
    ]
