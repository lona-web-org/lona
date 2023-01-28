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

    async def get_computed_style(page):
        return await page.eval_on_selector(
            '#rendering-root > div',
            """
                element => {
                    const computedStyle = getComputedStyle(element);
                    const propertyNames = Array.from(computedStyle);
                    const values = {};

                    propertyNames.forEach(name => {
                        values[name] = computedStyle.getPropertyValue(name);
                    });

                    return values;
                }
            """,
        )

    def get_style():
        return context.server.state['rendering-root'][0].style

    async def check_default_styles(page):
        """
        All CSS properties have a specified default value.
        Because we use window.getComputedStyle() to determine CSS values,
        we are required to check our estimated defaults are correct.
        """

        computed_style = await get_computed_style(page)

        assert computed_style['top'] == 'auto'
        assert computed_style['right'] == 'auto'
        assert computed_style['bottom'] == 'auto'
        assert computed_style['left'] == 'auto'

    async def parse_json(page, locator):
        element = page.locator(locator)
        json_string = await element.inner_html()

        return json.loads(json_string)

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

        # CSS tests ###########################################################
        await check_default_styles(page)

        # 22 Set Style
        await next_step(page, 22)

        computed_style = await get_computed_style(page)

        assert computed_style['top'] == '1px'
        assert computed_style['right'] == '2px'
        assert computed_style['bottom'] == 'auto'
        assert computed_style['left'] == 'auto'

        # 23 Add Style
        await next_step(page, 23)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert computed_style['top'] == '1px'
        assert computed_style['right'] == '2px'
        assert computed_style['bottom'] == '3px'
        assert computed_style['left'] == 'auto'

        # 24 Remove Style
        await next_step(page, 24)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert 'top' not in style

        assert computed_style['top'] == 'auto'
        assert computed_style['right'] == '2px'
        assert computed_style['bottom'] == '3px'
        assert computed_style['left'] == 'auto'

        # 25 Reset Style
        await next_step(page, 25)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert 'right' not in style
        assert 'bottom' not in style

        assert computed_style['top'] == 'auto'
        assert computed_style['right'] == 'auto'
        assert computed_style['bottom'] == 'auto'
        assert computed_style['left'] == '4px'

        # 26 Clear Style
        await next_step(page, 26)
        await check_default_styles(page)

        # widget data tests ###################################################
        for step in range(27, 39):
            await next_step(page, step)

            server_widget_data = await parse_json(
                page,
                '#lona #server-widget-data',
            )

            client_widget_data = await parse_json(
                page,
                '#lona #client-widget-data',
            )

            assert server_widget_data == client_widget_data

        # legacy widgets tests ################################################
        # TODO: remove in 2.0

        if get_client_version() != 1:
            return

        for step in range(39, 45):
            await next_step(page, step)

            client_html_string = await rendering_root_element.inner_html()

            client_html = HTML(client_html_string)
            server_html = HTML(str(context.server.state['rendering-root']))[0]

            assert client_html.nodes == server_html.nodes
