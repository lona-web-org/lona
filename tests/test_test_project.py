async def test_test_project(request, lona_project_context):
    import os

    from playwright.async_api import async_playwright

    TEST_PROJECT_PATH = os.path.join(request.fspath, '../../test_project')

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())
        await page.wait_for_selector('#lona>h2:has-text("View Types")')
