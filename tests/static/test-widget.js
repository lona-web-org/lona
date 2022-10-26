class TestWidget {
    constructor(lona_window) {
        this.lona_window = lona_window;
    };

    _dump_data() {
        this.root_node.innerHTML = JSON.stringify(this.data);
    };

    setup() {
        this._dump_data();
    };

    data_updated() {
        this._dump_data();
    };
};

Lona.register_widget_class('test-widget', TestWidget);