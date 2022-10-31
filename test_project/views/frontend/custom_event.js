function CustomEventWidget(lona_window) {
    this.lona_window = lona_window;

    this._patch_buttons = function() {
        var node = this.nodes[0].querySelector('#node-event');

        node.onclick = function(event) {
            lona_window.fire_input_event(node, 'custom-event', {foo: 'bar'});
        };

        this.nodes[0].querySelector('#non-node-event').onclick = function(event) {
            lona_window.fire_input_event(undefined, 'custom-event', {foo: 'bar'});
        };
    };

    this.setup = function() {
        var lona_window = this.lona_window;

        this._patch_buttons();
    };
};

Lona.register_widget_class('custom_event', CustomEventWidget);