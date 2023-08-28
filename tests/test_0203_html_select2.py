def test_option2():
    from lona.html import Option2

    option = Option2('Foo', value='foo')

    assert option.get_text() == 'Foo'
    assert option.value == 'foo'

    # selected
    option = Option2()

    assert not option.selected
    assert 'selected' not in option.attributes

    option.selected = True

    assert option.selected
    assert 'selected' in option.attributes

    option = Option2(selected=True)

    assert option.selected

    # disabled
    option = Option2()

    assert not option.disabled
    assert 'disabled' not in option.attributes

    option.disabled = True

    assert option.disabled
    assert 'disabled' in option.attributes

    option = Option2(disabled=True)

    assert option.disabled


def test_select2():
    import pytest

    from lona.html import Select2, Option2

    # basic API ###############################################################
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
        Option2('Baz', value='baz'),
    )

    assert not select.multiple

    # options
    assert len(select.nodes) == 3

    for option in select.nodes:
        assert type(option) is Option2
        assert 'selected' not in option.attributes

    # values
    assert select.value == 'foo'
    assert select.values == ('foo', 'bar', 'baz')

    select.value = 'bar'

    assert select.value == 'bar'

    assert not select.nodes[0].selected
    assert 'selected' not in select.nodes[0].attributes

    assert select.nodes[1].selected
    assert 'selected' in select.nodes[1].attributes

    assert not select.nodes[2].selected
    assert 'selected' not in select.nodes[2].attributes

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
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar', selected=True),
        Option2('Baz', value='baz'),
    )

    assert select.value == 'bar'
    assert select.values == ('foo', 'bar', 'baz')

    # multi select ############################################################
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
        Option2('Baz', value='baz'),
        multiple=True,
    )

    assert select.values == ('foo', 'bar', 'baz')
    assert select.value == ()

    select.value = ['foo', 'bar']

    assert select.value == ('foo', 'bar')
    assert select.values == ('foo', 'bar', 'baz')

    # multi select: pre selected values #######################################
    select = Select2(
        Option2('Foo', value='foo', selected=True),
        Option2('Bar', value='bar', selected=True),
        Option2('Baz', value='baz'),
        multiple=True,
    )

    assert select.value == ('foo', 'bar')
    assert select.values == ('foo', 'bar', 'baz')

    # helper ##################################################################
    # add_option
    select = Select2()

    select.add_option(
        Option2('Foo', value='foo'),
    )

    assert select.values == ('foo', )
    assert len(select.nodes) == 1

    # remove_option
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
    )

    select.remove_option(select[0])

    assert select.values == ('bar', )
    assert len(select.nodes) == 1

    # clear_options
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
        Option2('Baz', value='baz'),
    )

    select.clear_options()

    assert select.values == ()
    assert len(select.nodes) == 0

    # select all
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
        Option2('Baz', value='baz'),
    )

    select.select_all()

    assert select.value == 'foo'

    # select all, multi select
    select = Select2(
        Option2('Foo', value='foo'),
        Option2('Bar', value='bar'),
        Option2('Baz', value='baz'),
        multiple=True,
    )

    select.select_all()

    assert select.value == ('foo', 'bar', 'baz')

    # select none
    select = Select2(
        Option2('Foo', value='foo', selected=True),
        Option2('Bar', value='bar', selected=True),
        Option2('Baz', value='baz', selected=True),
    )

    select.select_none()

    assert select.value == 'foo'

    # select none, multi select
    select = Select2(
        Option2('Foo', value='foo', selected=True),
        Option2('Bar', value='bar', selected=True),
        Option2('Baz', value='baz', selected=True),
        multiple=True,
    )

    select.select_none()

    assert select.value == ()
