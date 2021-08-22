

Using Traditional HTML
======================

When defining big node trees or integrating third-party libraries its often
simpler to use traditional HTML syntax.

.. code-block:: python

    from lona.html import HTML
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            bootstrap_modal = HTML("""
                <div class="modal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Modal title</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p>Modal body text goes here.</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary">Save changes</button>
                            </div>
                        </div>
                    </div>
                </div>
            """)

            modal_body = bootstrap_modal.query_selector('div.modal-body')
            modal_footer = bootstrap_modal.query_selector('div.modal-footer')

            modal_body.set_text('Hello World')

**More information:**
`Using HTML Strings </end-user-documentation/html.html#using-html-strings>`_,
`Selectors </end-user-documentation/html.html#selectors>`_