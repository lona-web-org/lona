Lona.LonaWindowShim = function(lona_context, lona_window, widget_id) {
    this.lona_context = lona_context;

    this._lona_window = lona_window;
    this._widget_id = widget_id;

    this.fire_input_event = function(node, event_type, data) {
        return this._lona_window._input_event_handler.fire_input_event(
            this._widget_id,
            node,
            event_type,
            data,
        );
    };

    this.set_html = function(html) {
        if(this._lona_window._view_running) {
            throw('RuntimeError: cannot set HTML while a view is running');
        };

        this._lona_window._root.innerHTML = html;
    };
};
