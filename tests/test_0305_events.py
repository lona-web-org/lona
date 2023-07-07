import pytest


@pytest.mark.parametrize('client_version', [1, 2])
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
async def test_input_events(
        browser_name,
        client_version,
        lona_project_context,
):

    """
    This test tests all available input event types using the test-project
    URL /events/inputs/.
    """

    import os

    from playwright.async_api import async_playwright

    TEST_PROJECT_PATH = os.path.join(__file__, '../../test_project')

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
        settings_post_overrides={
            'CLIENT_VERSION': client_version,
        },
    )

    async def empty_console(page):
        await page.click('#reset-console')
        await page.wait_for_selector('#console:has-text("[EMPTY]")')

    async def event_logged(page):
        await page.wait_for_selector('#console:has-text("Time: ")')

    def get_node(element_id):
        return context.server.state['events'][element_id]

    def get_event():
        return context.server.state['events']['event']

    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url('/events/inputs/'))

        # click events ########################################################
        for element_id in ('#button', '#link', '#div'):
            await empty_console(page)

            await page.click(element_id)
            await event_logged(page)

            node = get_node(element_id)
            event = get_event()

            assert event.name == 'click'
            assert node is event.node

        # change events #######################################################
        # text input
        await empty_console(page)

        assert get_node('#text-input').value == ''

        await page.fill('#text-input', 'foo')
        await event_logged(page)

        node = get_node('#text-input')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == 'foo'

        # number input
        await empty_console(page)

        assert get_node('#number-input').value is None

        await page.fill('#number-input', '10')
        await event_logged(page)

        node = get_node('#number-input')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == 10.0

        # checkbox
        await empty_console(page)

        assert get_node('#check-box').value is False

        await page.check('#check-box')
        await event_logged(page)

        node = get_node('#check-box')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value is True

        # text area
        await empty_console(page)

        assert get_node('#text-area').value == ''

        await page.fill('#text-area', 'foo')
        await event_logged(page)

        node = get_node('#text-area')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == 'foo'

        # select
        await empty_console(page)

        assert get_node('#select').value == '1'

        await page.locator('#select').select_option('Option 2')
        await event_logged(page)

        node = get_node('#select')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == '2.0'

        # select2
        await empty_console(page)

        assert get_node('#select-2').value == 1

        await page.locator('#select-2').select_option('Option 2')
        await event_logged(page)

        node = get_node('#select-2')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == 2.0

        # multi select
        await empty_console(page)

        assert get_node('#multi-select').value == []

        await page.locator('#multi-select').select_option([
            'Option 1',
            'Option 2',
        ])

        await event_logged(page)

        node = get_node('#multi-select')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == ['1', '2.0']

        # multi select2
        await empty_console(page)

        assert get_node('#multi-select-2').value == ()

        await page.locator('#multi-select-2').select_option([
            'Option 1',
            'Option 2',
        ])

        await event_logged(page)

        node = get_node('#multi-select-2')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == (1, 2.0)

        # radio group
        await empty_console(page)

        assert get_node('#radio-group').value is None

        await page.locator('#radio-group').get_by_label('Option 2').check()
        await event_logged(page)

        node = get_node('#radio-group')
        event = get_event()

        assert event.name == 'change'
        assert event.node is node
        assert node.value == 2.0

        # focus events ########################################################
        await empty_console(page)

        await page.focus('#text-input-focus')
        await event_logged(page)

        node = get_node('#text-input-focus')
        event = get_event()

        assert event.name == 'focus'
        assert event.node is node

        # blur events #########################################################
        await empty_console(page)

        element = page.locator('#text-input-blur')

        await element.focus()
        await element.blur()
        await event_logged(page)

        node = get_node('#text-input-blur')
        event = get_event()

        assert event.name == 'blur'
        assert event.node is node
