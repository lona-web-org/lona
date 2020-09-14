import pytest


@pytest.mark.skip('This test is broken currently')
def test_constants():
    from lona.protocol import ExitCode, Method, InputEventType

    ExitCode.SUCCESS == 0
    ExitCode.INVALID_MESSAGE == 1
    ExitCode.INVALID_METHOD == 2

    Method.VIEW == 11
    Method.REDIRECT == 12
    Method.HTML == 13
    Method.INPUT_EVENT == 14
    Method.DESKTOP_NOTIFICATION == 15

    InputEventType.CLICK == 21
    InputEventType.CHANGE == 22
    InputEventType.SUBMIT == 23
    InputEventType.RESET == 24


@pytest.mark.skip('This test is broken currently')
def test_message_decoding():
    from lona.protocol import (
        InputEventType,  # because of this import
        decode_message,
        ExitCode,
        Method,
    )

    # valid view
    message = [Method.VIEW, '/index.html']
    exit_code, method, url, payload = decode_message(message)

    assert exit_code == ExitCode.SUCCESS
    assert method == Method.VIEW
    assert url == '/index.html'
    assert payload is None

    # valid input event with lona-node-id
    message = [Method.INPUT_EVENT, '/index.html',
               InputEventType.CLICK, 123456789]

    exit_code, method, url, payload = decode_message(message)

    assert exit_code == ExitCode.SUCCESS
    assert method == Method.INPUT_EVENT
    assert url == '/index.html'
    assert payload == [InputEventType.CLICK, 123456789]

    # valid input event without lona-node-id
    message = [Method.INPUT_EVENT, '/index.html',
               InputEventType.CLICK, None, 'div', 'id1 id2', 'class1 class2']

    exit_code, method, url, payload = decode_message(message)

    assert exit_code == ExitCode.SUCCESS
    assert method == Method.INPUT_EVENT
    assert url == '/index.html'

    assert payload == [
        InputEventType.CLICK, None, 'div', 'id1 id2', 'class1 class2']


@pytest.mark.skip('This test is broken currently')
def test_input_event_decoding():
    from lona.protocol import (
        InputEventType,
        InputEvent,  # because of this import
    )

    # click event with lona-node-id
    input_event = InputEvent([InputEventType.CLICK, 123456789])

    assert input_event.node_tree is None
    assert input_event.node is None
    assert input_event.widgets == []

    assert input_event.name == 'click'
    assert input_event.lona_node_id == 123456789
    assert input_event.tag_name is None
    assert input_event.node_id is None
    assert input_event.node_class is None

    assert input_event.node_id_list == []
    assert input_event.node_class_list == []

    # click event without lona-node-id
    input_event = InputEvent(
        [InputEventType.CLICK, None, 'div', 'id1 id2', 'class1 class2'])

    assert input_event.node_tree is None
    assert input_event.node is None
    assert input_event.widgets == []

    assert input_event.name == 'click'
    assert input_event.lona_node_id is None
    assert input_event.tag_name == 'div'
    assert input_event.node_id == 'id1 id2'
    assert input_event.node_class == 'class1 class2'

    assert input_event.node_id_list == ['id1', 'id2']
    assert input_event.node_class_list == ['class1', 'class2']

    assert input_event.node_has_id('id1')
    assert not input_event.node_has_id('id3')

    assert input_event.node_has_class('class1')
    assert not input_event.node_has_class('class3')


@pytest.mark.skip('This test is broken currently')
def test_html_encoding():
    from lona.protocol import Method, encode_html

    # input events, HTML string
    message = encode_html('/index.html', '<div></div>', input_events=True)

    assert isinstance(message, list)
    assert message[0] == Method.HTML
    assert message[1] == '/index.html'
    assert message[2] == '<div></div>'
    assert message[3] is True

    # no input events, HTML updates
    message = encode_html('/index.html', {}, input_events=False)

    assert isinstance(message, list)
    assert message[0] == Method.HTML
    assert message[1] == '/index.html'
    assert message[2] == {}
    assert message[3] is False


@pytest.mark.skip('This test is broken currently')
def test_redirect_encoding():
    from lona.protocol import Method, encode_redirect

    # interactive
    message = encode_redirect('/index.html', interactive=True)

    assert message[0] == Method.REDIRECT
    assert message[1] == '/index.html'
    assert message[2] is True

    # non interactive
    message = encode_redirect('/index.html', interactive=False)

    assert message[0] == Method.REDIRECT
    assert message[1] == '/index.html'
    assert message[2] is False
