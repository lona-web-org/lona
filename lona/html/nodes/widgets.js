class LonaRawHtmlWidget {
    constructor(lonaWindow, rootNode, widgetData) {
        this.lonaWindow = lonaWindow;
        this.rootNode = rootNode;

        this.render(widgetData);
    }

    onDataUpdated(widgetData) {
        this.render(widgetData);
    }

    render(widgetData) {
        this.rootNode.innerHTML = widgetData.data.inner_html;
    }
}


Lona.register_widget_class('lona.RawHtmlWidget', LonaRawHtmlWidget);
