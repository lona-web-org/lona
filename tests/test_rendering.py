import pytest


@pytest.mark.parametrize('rendering_setup', [
    'chromium:client-1',
    'chromium:client-2',
    'firefox:client-1',
    'firefox:client-2',
    'webkit:client-1',
    'webkit:client-2',
])
async def test_rendering(rendering_setup, lona_project_context):
    """
    This test tests all client side rendering features, using the rendering
    test view in the test project.

    The test has two phases: DOM tests, where DOM elements get manipulated, and
    a CSS phase, where the browsers style API gets used.

    The DOM phase is pretty simple and straightforward: The view creates and
    manipulates a simple DOM tree and sends it to the client to render it. The
    rendered HTML has to be equal to the servers representation of the DOM.

    In the CSS phase we can't just check the servers style attributes against
    the clients style attributes, because Lona does not define defaults for
    properties that are not set by the user. In the browser all CSS properties
    always have a value.

    TODO: remove in 2.0
    This test has a last phase, that tests node-list operations using the
    legacy widget API.
    """

    import json
    import os

    from playwright.async_api import async_playwright

    from lona.compat import get_client_version
    from lona.html import Widget, HTML

    TEST_PROJECT_PATH = os.path.join(__file__, '../../test_project')

    browser_name, client_version = rendering_setup.split(':')
    client_version = int(client_version[7:])

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
        settings_post_overrides={
            'CLIENT_VERSION': client_version,
        },
    )

    async def next_step(page, number):
        await page.locator('#lona #next-step').click()
        await page.wait_for_selector(f'#lona #step-label>#current:has-text("{number}")')

    async def get_client_style(page):
        return await page.eval_on_selector(
            '#rendering-root > div',
            """
                element => {
                    const propertyNames = Array.from(element.style);
                    const values = {};

                    propertyNames.forEach(name => {
                        values[name] = element.style.getPropertyValue(name);
                    });

                    return values;
                }
            """,
        )

    def get_server_style():
        return context.server.state['rendering-root'][0].style

    async def check_empty_client_style(page):
        client_style = await get_client_style(page)

        assert 'top' not in client_style
        assert 'right' not in client_style
        assert 'bottom' not in client_style
        assert 'left' not in client_style
        assert '--non-standard' not in client_style

    async def parse_json(page, locator):
        element = page.locator(locator)
        json_string = await element.inner_html()

        return json.loads(json_string)

    async def get_widget_hooks(page):
        element = page.locator('#lona #rendering-root #widget-hooks')
        widget_hooks = await element.inner_html()

        return widget_hooks.strip()

    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # start rendering test view
        await page.goto(context.make_url('/frontend/rendering/'))
        await page.wait_for_selector('#lona h2:has-text("Rendering Test")')

        rendering_root_element = page.locator('#lona #rendering-root')

        # DOM tests ###########################################################
        for step in range(1, 22):
            await next_step(page, step)

            # get rendered html
            html_string = await rendering_root_element.inner_html()

            # parse and compare html
            html = HTML(f'<div id="rendering-root">{html_string}</div>')

            if isinstance(html, Widget):
                html = html[0]

            assert html.nodes == context.server.state['rendering-root'].nodes

        # html symbols
        await next_step(page, 22)

        html_string = await rendering_root_element.inner_html()

        assert html_string == '€€€'

        # CSS tests ###########################################################

        # 23 Empty style
        await next_step(page, 23)
        await check_empty_client_style(page)

        # 24 Set Style
        await next_step(page, 24)

        client_style = await get_client_style(page)

        assert client_style['top'] == '1px'
        assert client_style['right'] == '2px'
        assert client_style['--non-standard'] == '3'

        # 25 Add Style
        await next_step(page, 25)

        client_style = await get_client_style(page)
        style = get_server_style()

        assert client_style['top'] == '1px'
        assert client_style['right'] == '2px'
        assert client_style['--non-standard'] == '3'
        assert client_style['bottom'] == '3px'

        # 26 Remove Style
        await next_step(page, 26)

        client_style = await get_client_style(page)
        style = get_server_style()

        assert 'top' not in style

        assert client_style['right'] == '2px'
        assert client_style['bottom'] == '3px'
        assert client_style['--non-standard'] == '3'

        # 27 Reset Style
        await next_step(page, 27)

        client_style = await get_client_style(page)
        style = get_server_style()

        assert 'right' not in style
        assert 'bottom' not in style

        assert client_style['left'] == '4px'

        # 28 Clear Style
        await next_step(page, 28)
        await check_empty_client_style(page)

        # legacy widget API ###################################################
        # TODO: remove in 2.0
        for step in range(29, 41):
            await next_step(page, step)

            # widget hooks
            assert (await get_widget_hooks(page)) == 'constructor,setup'

            # widget data
            server_widget_data = await parse_json(
                page,
                '#lona #rendering-root #server-widget-data',
            )

            client_widget_data = await parse_json(
                page,
                '#lona #rendering-root #client-widget-data',
            )

            assert server_widget_data == client_widget_data

        # destroy
        await next_step(page, 41)

        assert (await get_widget_hooks(page)) == 'constructor,setup,deconstruct'

        # widget API ##########################################################
        for step in range(42, 54):
            await next_step(page, step)

            # widget hooks
            assert (await get_widget_hooks(page)) == 'constructor'

            # widget data
            server_widget_data = await parse_json(
                page,
                '#lona #rendering-root #server-widget-data',
            )

            client_widget_data = await parse_json(
                page,
                '#lona #rendering-root #client-widget-data',
            )

            assert server_widget_data == client_widget_data

        # destroy
        await next_step(page, 54)

        assert (await get_widget_hooks(page)) == 'constructor,destroy'

        # raw HTML tests ######################################################
        for step in range(55, 58):
            await next_step(page, step)

            client_html_string = await rendering_root_element.inner_html()

            client_html = HTML(client_html_string)
            server_html = HTML(str(context.server.state['rendering-root']))[0]

            assert client_html.nodes == server_html.nodes

        # legacy frontend widgets tests #######################################
        # TODO: remove in 2.0

        if get_client_version() != 1:
            return

        for step in range(58, 64):
            await next_step(page, step)

            client_html_string = await rendering_root_element.inner_html()

            client_html = HTML(client_html_string)
            server_html = HTML(str(context.server.state['rendering-root']))[0]

            assert client_html.nodes == server_html.nodes

        # legacy frontend widgets data tests ##################################
        for step in range(64, 76):
            await next_step(page, step)

            # widget hooks
            assert (await get_widget_hooks(page)) == 'constructor,setup'

            # widget data
            server_widget_data = await parse_json(
                page,
                '#lona #rendering-root #server-widget-data',
            )

            client_widget_data = await parse_json(
                page,
                '#lona #rendering-root #client-widget-data',
            )

            assert server_widget_data == client_widget_data

        # destroy
        await next_step(page, 76)

        assert (await get_widget_hooks(page)) == 'constructor,setup,deconstruct'
