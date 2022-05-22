Lona.LonaWindowShim = class LonaWindowShim {
    constructor(lona_context, lona_window, widget_id) {
        this.lona_context = lona_context;

        this._lona_window = lona_window;
        this._widget_id = widget_id;
    };

    fire_input_event(node, event_type, data) {
        return this._lona_window._input_event_handler.fire_input_event(
            node || this._widget_id,
            event_type,
            data,
        );
    };

    set_html(html) {
        if(this._lona_window._view_running) {
            throw('RuntimeError: cannot set HTML while a view is running');
        };

        this._lona_window._root.innerHTML = html;
    };
};
