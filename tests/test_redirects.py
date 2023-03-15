import pytest


@pytest.mark.parametrize('client_version', [1, 2])
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
@pytest.mark.parametrize('method', ['link', 'redirect', 'http-redirect'])
async def test_redirects(
        method,
        browser_name,
        client_version,
        lona_project_context,
):

    import os

    from playwright.async_api import async_playwright

    TEST_PROJECT_PATH = os.path.join(__file__, '../../test_project')
    BASE_URL = '/frontend/redirects'

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
        settings_post_overrides={
            'CLIENT_VERSION': client_version,
        },
    )

    datasets = [

        # absolute url
        (f'{BASE_URL}/foo/bar/baz/', '/foo', '/foo'),

        # relative urls
        (f'{BASE_URL}/foo/bar/baz', '.', f'{BASE_URL}/foo/bar/'),
        (f'{BASE_URL}/foo/bar/baz/', '.', f'{BASE_URL}/foo/bar/baz/'),

        # relative forward urls
        (f'{BASE_URL}/foo/bar/baz', './foo', f'{BASE_URL}/foo/bar/foo'),
        (f'{BASE_URL}/foo/bar/baz/', './foo', f'{BASE_URL}/foo/bar/baz/foo'),

        # relative backward urls
        (f'{BASE_URL}/foo/bar/baz', '..', f'{BASE_URL}/foo/'),
        (f'{BASE_URL}/foo/bar/baz/', '..', f'{BASE_URL}/foo/bar/'),
    ]

    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        browser_context = await browser.new_context()

        for raw_initial_url, redirect_url, success_url in datasets:
            page = await browser_context.new_page()

            # initial load
            initial_url = context.make_url(raw_initial_url)

            await page.goto(initial_url)
            await page.wait_for_url(initial_url)

            # trigger redirect
            await page.fill('input#url', redirect_url)
            await page.wait_for_selector(f'a#link[href="{redirect_url}"]')

            if method == 'link':
                await page.click('a#link')

            elif method == 'redirect':
                await page.click('button#redirect')

            elif method == 'http-redirect':
                await page.click('button#http-redirect')

            # wait for success url
            await page.wait_for_url(success_url)

            # close page
            await page.close()
