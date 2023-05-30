from lona.html import NumberInput, HTML1


def test_default_properties():
    node = NumberInput()

    assert node.value is None
    assert node.min is None
    assert node.max is None
    assert node.step is None


def test_initial_value():
    node = NumberInput(value=12.3)

    assert node.value == 12.3


def test_change_value():
    node = NumberInput()
    node.value = 12.3

    assert node.value == 12.3


def test_parsing_no_attributes():
    node = HTML1('<input type="number"/>')[0]

    assert node.value is None
    assert node.min is None
    assert node.max is None
    assert node.step is None


def test_parsing_int_value():
    node = HTML1('<input type="number" value="123"/>')[0]

    assert node.value == 123


def test_parsing_float_value():
    node = HTML1('<input type="number" value="12.3"/>')[0]

    assert node.value == 12.3


def test_parsing_broken_step():
    node = HTML1('<input type="number" value="123" step="abc"/>')[0]

    assert node.value == 123
    assert node.step is None


def test_parsing_int_step():
    node = HTML1('<input type="number" value="12.3" step="3"/>')[0]

    assert node.value == 12.3
    assert node.step == 3


def test_parsing_float_step():
    node = HTML1('<input type="number" value="12.3" step="0.1"/>')[0]

    assert node.value == 12.3
    assert node.step == 0.1


def test_parsing_broken_value():
    node = HTML1('<input type="number" value="abc" step="0.1"/>')[0]

    assert node.raw_value == 'abc'
    assert node.value is None


def test_parsing_all_attributes():
    node = HTML1(
        '<input type="number" value="12.3" min="15.3" max="20.5" step="0.2"/>',
    )[0]

    assert node.value == 12.3
    assert node.min == 15.3
    assert node.max == 20.5
    assert node.step == 0.2
