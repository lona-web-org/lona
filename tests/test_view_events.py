from lona.pytest import eventually
from lona import View


def setup_app(app):

    @app.route('/view-1/')
    class View1(View):
        def handle_request(self, request):
            if 'fire' in request.GET:
                self.fire_view_event('view1', {'view1': True})

        def on_view_event(self, view_event):
            self.server.state['view1'].append(
                (view_event.name, view_event.data),
            )

    @app.route('/view-2/')
    class View2(View):
        def handle_request(self, request):
            if 'fire' in request.GET:
                self.fire_view_event('view2', {'view2': True})

        def on_view_event(self, view_event):
            self.server.state['view2'].append(
                (view_event.name, view_event.data),
            )

    @app.route('/broadcast/')
    class FireBroadcastEvent(View):
        def handle_request(self, request):
            self.server.fire_view_event('broadcast', {'broadcast': True})


async def test_view_events(lona_app_context):
    """
    This test tests view events by creating two views that send events to all
    of their instances, and one view that sends events to all views in the
    system.
    The test is successful if both of the first two views only received their
    own events, and the broadcast events, and no event from view 1 leaked to
    view 2 or vice versa.
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:
        context.server.state['view1'] = []
        context.server.state['view2'] = []

        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()

        # view 1
        view1_page1 = await browser_context.new_page()
        view1_page2 = await browser_context.new_page()
        view1_page3 = await browser_context.new_page()

        await view1_page1.goto(context.make_url('/view-1/'))
        await view1_page2.goto(context.make_url('/view-1/'))
        await view1_page3.goto(context.make_url('/view-1/?fire'))

        # view 2
        view2_page1 = await browser_context.new_page()
        view2_page2 = await browser_context.new_page()
        view2_page3 = await browser_context.new_page()

        await view2_page1.goto(context.make_url('/view-2/'))
        await view2_page2.goto(context.make_url('/view-2/'))
        await view2_page3.goto(context.make_url('/view-2/?fire'))

        # broadcast
        broadcast_page = await browser_context.new_page()

        await broadcast_page.goto(context.make_url('/broadcast/'))

        # check captured events
        for attempt in eventually():
            async with attempt:
                assert sorted(context.server.state['view1']) == [
                    ('broadcast', {'broadcast': True}),
                    ('broadcast', {'broadcast': True}),
                    ('broadcast', {'broadcast': True}),
                    ('view1', {'view1': True}),
                    ('view1', {'view1': True}),
                    ('view1', {'view1': True}),
                ]

                assert sorted(context.server.state['view2']) == [
                    ('broadcast', {'broadcast': True}),
                    ('broadcast', {'broadcast': True}),
                    ('broadcast', {'broadcast': True}),
                    ('view2', {'view2': True}),
                    ('view2', {'view2': True}),
                    ('view2', {'view2': True}),
                ]
