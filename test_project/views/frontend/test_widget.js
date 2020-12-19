function TestWidget(lona_window) {
    this.lona_window = lona_window;

    this.setup = function() {
        console.log('>> setup', this.nodes);
    };

    this.nodes_updated = function() {
        console.log('>> nodes updated', this.nodes);
    };

    this.data_updated = function() {
        this.nodes[1].innerHTML = JSON.stringify(this.data);
    };
};

Lona.register_widget_class('test_widget', TestWidget);
