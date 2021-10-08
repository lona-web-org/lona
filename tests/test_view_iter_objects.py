from lona.pytest import eventually
from lona import LonaView


async def test_view_iter_objects(lona_app_context):
    """
    This test tests LonaView.iter_objects() with theese steps:

     - Creating two views
     - Opening 3 tabs on view 1
     - Opening 2 tabs on view 2
     - Count view objects of view 1 and 2 and check view classes
     - Closing 1 tab on view 1
     - Closing 1 tab on view 2
     - Count view objects of view 1 and 2 and check view classes
    """

    from playwright.async_api import async_playwright

    # setup views
    class View1(LonaView):
        pass

    class View2(LonaView):
        pass

    def setup_app(app):
        app.route('/view-1/')(View1)
        app.route('/view-2/')(View2)

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()

        # view 1
        view1_page1 = await browser_context.new_page()
        view1_page2 = await browser_context.new_page()
        view1_page3 = await browser_context.new_page()

        await view1_page1.goto(context.make_url('/view-1/'))
        await view1_page2.goto(context.make_url('/view-1/'))
        await view1_page3.goto(context.make_url('/view-1/'))

        # view 2
        view2_page1 = await browser_context.new_page()
        view2_page2 = await browser_context.new_page()

        await view2_page1.goto(context.make_url('/view-2/'))
        await view2_page2.goto(context.make_url('/view-2/'))

        # count view objects
        for attempt in eventually():
            async with attempt:

                # view 1
                view_objects = list(View1.iter_objects())

                assert len(view_objects) == 3

                for view_object in view_objects:
                    assert view_object.__class__ == View1

                # view 2
                view_objects = list(View2.iter_objects())

                assert len(view_objects) == 2

                for view_object in view_objects:
                    assert view_object.__class__ == View2

        # close two tabs
        await view1_page3.goto(context.make_url('/'))
        await view2_page2.goto(context.make_url('/'))

        # recount view objects
        for attempt in eventually():
            async with attempt:

                # view 1
                view_objects = list(View1.iter_objects())

                assert len(view_objects) == 2

                for view_object in view_objects:
                    assert view_object.__class__ == View1

                # view 2
                view_objects = list(View2.iter_objects())

                assert len(view_objects) == 1

                for view_object in view_objects:
                    assert view_object.__class__ == View2
