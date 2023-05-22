def save_message(message_list):
    def _save_message(message):
        if message.topic.startswith('lona.'):
            return

        message_list.append(message)

        if message.data.get('crash', False):
            raise RuntimeError()

    return _save_message


def do_nothing(*args, **kwargs):
    pass


async def test_subscribe_and_unsubscribe(lona_app_context):
    import pytest

    from lona import Channel

    await lona_app_context(do_nothing)

    # not subscribed channels
    channel = Channel('channel.1')

    assert 'channel.1' not in Channel._channels

    # subscribe on init
    channel = Channel('channel.2', do_nothing)

    assert 'channel.2' in Channel._channels
    assert channel in Channel._channels['channel.2']

    # subscribe using method
    channel = Channel('channel.3')

    channel.subscribe(do_nothing)

    with pytest.raises(RuntimeError):
        channel.subscribe(do_nothing)

    assert 'channel.3' in Channel._channels
    assert channel in Channel._channels['channel.3']

    # unsubscribe
    channel = Channel('channel.4', do_nothing)

    assert 'channel.4' in Channel._channels
    assert channel in Channel._channels['channel.4']

    channel.unsubscribe()

    assert 'channel.4' not in Channel._channels


async def test_message_expiry(lona_app_context):
    from datetime import timedelta, datetime

    from lona.pytest import eventually
    from lona import Channel

    await lona_app_context(do_nothing)

    messages = []
    channel = Channel('channel.1', save_message(messages))

    # expired message
    message_1 = channel.send(
        message_data={'message': 'test1'},
        expiry=datetime(1970, 1, 1),
    )

    for attempt in eventually():
        async with attempt:
            assert message_1.is_dropped()
            assert len(messages) == 0

    # non expired message
    message_2 = channel.send(
        message_data={'message': 'test2'},
        expiry=timedelta(hours=1),
    )

    for attempt in eventually():
        async with attempt:
            assert len(messages) == 1
            assert not message_2.is_dropped()


async def test_message_integrity(lona_app_context):
    from lona.pytest import eventually
    from lona import Channel

    await lona_app_context(do_nothing)

    messages = []
    channel = Channel('channel.1', save_message(messages))

    message = {
        'immutable': 'test1',
        'mutable': ['test1'],
    }

    # send message
    channel.send(message)

    # await message
    for attempt in eventually():
        async with attempt:
            assert len(messages) == 1
            assert messages[0].data['immutable'] == 'test1'
            assert messages[0].data['mutable'] == ['test1']

    # change original message
    message['immutable'] = 'test2'
    message['mutable'][0] = 'test2'

    # run checks
    assert messages[0].data is not message
    assert messages[0].data['immutable'] == 'test1'
    assert messages[0].data['mutable'] == ['test2']


async def test_topic_matching(lona_app_context):
    from lona.pytest import eventually
    from lona import Channel

    await lona_app_context(do_nothing)

    channel_1_messages = []
    channel_2_messages = []
    channel_broadcast_messages = []
    broadcast_messages = []

    def clear_messages():
        channel_1_messages.clear()
        channel_2_messages.clear()
        channel_broadcast_messages.clear()
        broadcast_messages.clear()

    Channel('channel.1', save_message(channel_1_messages))
    Channel('channel.2', save_message(channel_2_messages))
    Channel('channel.*', save_message(channel_broadcast_messages))
    Channel('*', save_message(broadcast_messages))

    # direct message
    clear_messages()
    Channel('channel.1').send({'message': 'test1'})

    for attempt in eventually():
        async with attempt:
            assert len(channel_1_messages) == 1
            assert len(channel_2_messages) == 0
            assert len(channel_broadcast_messages) == 1
            assert len(broadcast_messages) == 1

            # channel 1
            assert channel_1_messages[0].topic == 'channel.1'
            assert channel_1_messages[0].data == {'message': 'test1'}

            # channel broadcast
            assert channel_broadcast_messages[0].topic == 'channel.1'
            assert channel_broadcast_messages[0].data == {'message': 'test1'}

            # broadcast
            assert broadcast_messages[0].topic == 'channel.1'
            assert broadcast_messages[0].data == {'message': 'test1'}

    clear_messages()
    Channel('channel.2').send({'message': 'test2'})

    for attempt in eventually():
        async with attempt:
            assert len(channel_1_messages) == 0
            assert len(channel_2_messages) == 1
            assert len(channel_broadcast_messages) == 1
            assert len(broadcast_messages) == 1

            # channel 2
            assert channel_2_messages[0].topic == 'channel.2'
            assert channel_2_messages[0].data == {'message': 'test2'}

            # channel broadcast
            assert channel_broadcast_messages[0].topic == 'channel.2'
            assert channel_broadcast_messages[0].data == {'message': 'test2'}

            # broadcast
            assert broadcast_messages[0].topic == 'channel.2'
            assert broadcast_messages[0].data == {'message': 'test2'}

    # channel broadcast message
    clear_messages()
    Channel('channel.*').send({'message': 'test3'})

    for attempt in eventually():
        async with attempt:
            assert len(channel_1_messages) == 1
            assert len(channel_2_messages) == 1
            assert len(channel_broadcast_messages) == 1
            assert len(broadcast_messages) == 1

            # channel 1
            assert channel_1_messages[0].topic == 'channel.*'
            assert channel_1_messages[0].data == {'message': 'test3'}

            # channel 2
            assert channel_2_messages[0].topic == 'channel.*'
            assert channel_2_messages[0].data == {'message': 'test3'}

            # channel broadcast
            assert channel_broadcast_messages[0].topic == 'channel.*'
            assert channel_broadcast_messages[0].data == {'message': 'test3'}

            # broadcast
            assert broadcast_messages[0].topic == 'channel.*'
            assert broadcast_messages[0].data == {'message': 'test3'}

    # broadcast message
    clear_messages()
    Channel('*').send({'message': 'test4'})

    for attempt in eventually():
        async with attempt:
            assert len(channel_1_messages) == 1
            assert len(channel_2_messages) == 1
            assert len(channel_broadcast_messages) == 1
            assert len(broadcast_messages) == 1

            # channel 1
            assert channel_1_messages[0].topic == '*'
            assert channel_1_messages[0].data == {'message': 'test4'}

            # channel 2
            assert channel_2_messages[0].topic == '*'
            assert channel_2_messages[0].data == {'message': 'test4'}

            # channel broadcast
            assert channel_broadcast_messages[0].topic == '*'
            assert channel_broadcast_messages[0].data == {'message': 'test4'}

            # broadcast
            assert broadcast_messages[0].topic == '*'
            assert broadcast_messages[0].data == {'message': 'test4'}


async def test_internal_topics(lona_app_context):
    from lona.pytest import eventually
    from lona import Channel

    await lona_app_context(do_nothing)

    messages = []

    def save_message(message):

        # skip test channel
        if (message.topic == 'lona.channels.subscribe' and
                message.data['topic'] == 'lona.*'):

            return

        messages.append(message)

    Channel('lona.*', save_message)

    messages.clear()

    # lona.channels.subscribe
    channel = Channel('channel.1', do_nothing)

    for attempt in eventually():
        async with attempt:
            assert len(messages) == 1
            assert messages[0].local is True
            assert messages[0].topic == 'lona.channels.subscribe'
            assert messages[0].data['topic'] == 'channel.1'

    # lona.channels.unsubscribe
    messages.clear()
    channel.unsubscribe()

    for attempt in eventually():
        async with attempt:
            assert len(messages) == 1
            assert messages[0].local is True
            assert messages[0].topic == 'lona.channels.unsubscribe'
            assert messages[0].data['topic'] == 'channel.1'


async def test_view_api(lona_app_context):
    from playwright.async_api import async_playwright

    from lona.pytest import eventually
    from lona import Channel, View

    messages = []

    def setup_app(app):

        @app.error_500_view
        class Error500InternalErrorView(View):
            def handle_request(self, request, exception):
                return 'INTERNAL ERROR'

        @app.route('/')
        class ChannelView(View):
            def handle_request(self, request):
                self.subscribe('channel.1', save_message(messages))

                return 'VIEW'

    context = await lona_app_context(setup_app)

    assert 'channel.1' not in Channel._channels

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()

        page = await browser_context.new_page()

        # subscribe to channel
        await page.goto(context.make_url('/'))

        for attempt in eventually():
            async with attempt:
                assert 'channel.1' in Channel._channels

        await page.wait_for_selector('#lona:has-text("VIEW")')

        Channel('channel.1').send({'message': 'test1'})

        for attempt in eventually():
            async with attempt:
                assert len(messages) == 1
                assert messages[0].data['message'] == 'test1'

        # crashing channel handler
        Channel('channel.1').send({'message': 'test2', 'crash': True})

        await page.wait_for_selector('#lona:has-text("INTERNAL ERROR")')

        for attempt in eventually():
            async with attempt:
                # the message should have come through, but the channel
                # should be unsubscribed by View.subscribe._handler

                assert len(messages) == 2
                assert messages[1].data['message'] == 'test2'
                assert 'channel.1' not in Channel._channels

        # unsubscribe channel
        await page.goto(context.make_url('/'))
        await page.wait_for_selector('#lona:has-text("VIEW")')

        Channel('channel.1').send({'message': 'test3'})

        for attempt in eventually():
            async with attempt:
                assert len(messages) == 3
                assert messages[2].data['message'] == 'test3'

        await page.close()

        for attempt in eventually():
            async with attempt:
                assert 'channel.1' not in Channel._channels
