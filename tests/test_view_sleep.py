async def test_view_sleep(lona_project_context):
    import os

    from playwright.async_api import async_playwright

    from lona.pytest import eventually

    TEST_PROJECT_PATH = os.path.join(__file__, '../../test_project')

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
    )

    # FIXME: this is only necessary because get parameters seem not to work
    # with the current playwright setup
    test_id = 'sleep-test-view'

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()

        page = await browser_context.new_page()

        # short sleep #########################################################
        await page.goto(context.make_url('/view-api/sleep'))
        await page.wait_for_selector('#lona h2:has-text("View.sleep()")')

        assert context.server.state[test_id]['state'] == 'Waiting for start'
        assert context.server.state[test_id]['started'] == '-'
        assert context.server.state[test_id]['stopped'] == '-'

        await page.fill('#seconds', '1')
        await page.click('#sleep')

        # wait for start
        for attempt in eventually():
            async with attempt:
                assert context.server.state[test_id]['started'] != '-'
                assert context.server.state[test_id]['stopped'] == '-'

        # wait for stop
        for attempt in eventually():
            async with attempt:
                assert context.server.state[test_id]['started'] != '-'
                assert context.server.state[test_id]['stopped'] != '-'

        # long, interrupted sleep #############################################
        await page.goto(context.make_url('/view-api/sleep'))
        await page.wait_for_selector('#lona h2:has-text("View.sleep()")')

        assert context.server.state[test_id]['state'] == 'Waiting for start'
        assert context.server.state[test_id]['started'] == '-'
        assert context.server.state[test_id]['stopped'] == '-'

        await page.fill('#seconds', '300')
        await page.click('#sleep')

        # wait for start
        for attempt in eventually():
            async with attempt:
                assert context.server.state[test_id]['started'] != '-'
                assert context.server.state[test_id]['stopped'] == '-'

        # close tab
        await page.close()

        for attempt in eventually():
            async with attempt:
                assert test_id not in context.server.state
