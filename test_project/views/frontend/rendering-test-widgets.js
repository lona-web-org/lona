class WidgetDataTestWidget {
    constructor(lona_window) {
        this.lona_window = lona_window;
    }

    render() {
        this.root_node.children[1].innerHTML = JSON.stringify(this.data);
    }

    setup() {
        this.render();
        console.log('>> setup', this.nodes);
    }

    deconstruct() {
        console.log('>> deconstruct', this.nodes);
    }

    nodes_updated() {
        console.log('>> nodes updated', this.nodes);
    }

    data_updated() {
        this.render();
    }
}

Lona.register_widget_class('WidgetDataTestWidget', WidgetDataTestWidget);
