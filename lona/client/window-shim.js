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
};
