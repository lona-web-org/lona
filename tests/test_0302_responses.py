import pytest


async def get_frontend_uptime(page):
    return (await page.locator('#application-started').all_text_contents())[0]


async def get_exception_info(page):
    info = {
        'type': '',
        'args': '',
    }

    await page.wait_for_selector('#lona h2:has-text("500")')

    info['type'] = (
        await page.locator('#exception-type').all_text_contents())[0]

    info['args'] = (
        await page.locator('#exception-args').all_text_contents())[0]

    return info


@pytest.mark.parametrize('url_prefix', ['dict-', ''])
@pytest.mark.parametrize('client_version', [1, 2])
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
async def test_interactive_responses(
        browser_name,
        client_version,
        url_prefix,
        lona_project_context,
):

    import os

    from playwright.async_api import async_playwright, expect

    from lona.pytest import eventually

    context = await lona_project_context(
        project_root=os.path.join(__file__, '../../test_project'),
        settings=['settings.py'],
        settings_post_overrides={
            'CLIENT_VERSION': client_version,
        },
    )

    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # empty response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#empty-response')
        await expect(page.locator('#lona')).to_be_empty()

        # node response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#node-response')
        await page.wait_for_selector('#lona p:has-text("Node Response")')

        # string response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#string-response')
        await page.wait_for_selector('#lona:has-text("String Response")')

        # template response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#template-response')
        await page.wait_for_selector('#lona h2:has-text("Template Response")')

        # template string response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#template-string-response')
        await page.wait_for_selector('#lona:has-text("Template String Response")')

        # redirect response
        url = f'/{url_prefix}responses/interactive/'

        await page.goto(context.make_url(url))
        await page.wait_for_url(url)

        frontend_uptime = await get_frontend_uptime(page)

        await page.click('#lona a#redirect-response')
        await page.wait_for_url('/')

        assert (await get_frontend_uptime(page)) == frontend_uptime

        # http redirect response
        url = f'/{url_prefix}responses/interactive/'

        await page.goto(context.make_url(url))
        await page.wait_for_url(url)

        frontend_uptime = await get_frontend_uptime(page)

        await page.click('#lona a#http-redirect-response')
        await page.wait_for_url('/')

        for attempt in eventually():
            async with attempt:
                assert (await get_frontend_uptime(page)) != frontend_uptime

        # file response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#file-response')

        exception_info = await get_exception_info(page)

        assert exception_info['type'] == 'RuntimeError'
        assert exception_info['args'] == "('JSON, binary and file responses and headers are only available in non-interactive mode',)"

        # json response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#json-response')

        exception_info = await get_exception_info(page)

        assert exception_info['type'] == 'RuntimeError'
        assert exception_info['args'] == "('JSON, binary and file responses and headers are only available in non-interactive mode',)"

        # binary response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#binary-response')

        exception_info = await get_exception_info(page)

        assert exception_info['type'] == 'RuntimeError'
        assert exception_info['args'] == "('JSON, binary and file responses and headers are only available in non-interactive mode',)"

        # custom headers response
        await page.goto(context.make_url(f'/{url_prefix}responses/interactive/'))
        await page.click('#lona a#custom-headers-response')

        exception_info = await get_exception_info(page)

        assert exception_info['type'] == 'RuntimeError'
        assert exception_info['args'] == "('JSON, binary and file responses and headers are only available in non-interactive mode',)"


@pytest.mark.parametrize('url_prefix', ['dict-', ''])
async def test_non_interactive_responses(url_prefix, lona_project_context):
    import os

    from aiohttp import ClientSession

    context = await lona_project_context(
        project_root=os.path.join(__file__, '../../test_project'),
        settings=['settings.py'],
    )

    async with ClientSession() as session:

        # empty response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/empty-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.text()) == ''

        # node response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/node-response')

        async with session.get(url) as response:
            assert response.status == 200

            text = await response.text()

            assert '<p' in text
            assert 'Node Response' in text

        # string response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/string-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.text()) == 'String Response'

        # template response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/template-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert '<h2>Template Response</h2>' in (await response.text())

        # template string response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/template-string-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.text()) == 'Template String Response'

        # redirect response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/redirect-response')

        async with session.get(url, allow_redirects=False) as response:
            assert response.status == 302
            assert response.headers['Location'] == '/'

        # http redirect response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/http-redirect-response')

        async with session.get(url, allow_redirects=False) as response:
            assert response.status == 302
            assert response.headers['Location'] == '/'

        # file response
        path = os.path.join(
            os.path.dirname(__file__),
            '../doc/content/logo.svg',
        )

        url = context.make_url(f'/{url_prefix}responses/non-interactive/file-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.content.read()) == open(path, 'rb').read()

        # json response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/json-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert response.content_type == 'application/json'
            assert (await response.json()) == {'foo': 'bar'}

        # binary response
        path = os.path.join(
            os.path.dirname(__file__),
            '../doc/content/logo.svg',
        )

        url = context.make_url(f'/{url_prefix}responses/non-interactive/binary-response')

        async with session.get(url) as response:
            assert response.status == 200
            assert response.content_type == 'image/svg+xml'
            assert (await response.content.read()) == open(path, 'rb').read()

        # custom headers response
        url = context.make_url(f'/{url_prefix}responses/non-interactive/custom-headers-response')

        async with session.get(url) as response:
            assert response.status == 418
            assert response.headers['HEADER-1'] == 'foo'
            assert response.headers['HEADER-2'] == 'bar'
