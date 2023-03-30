class LegacyWidgetApiTestWidget {
    // TODO: remove in 2.0

    // helper -----------------------------------------------------------------
    render() {
        let client_data;

        // legacy frontend widget
        if(this.nodes.length > 1) {
            client_data = this.nodes[1];

        } else {
            client_data = this.nodes[0].children[1];
        }

        client_data.innerHTML = JSON.stringify(this.data);
    }

    log_hook(name) {
        const element = this.lona_window.root_node.querySelector(
            '#widget-hooks',
        );

        if(!element) {
            return;
        }

        if(element.innerHTML != '') {
            element.innerHTML = `${element.innerHTML},`;
        }

        element.innerHTML = `${element.innerHTML}${name}`;
    }

    // hooks ------------------------------------------------------------------
    constructor(lona_window) {
        this.lona_window = lona_window;
        this.log_hook('constructor');
    }

    setup() {
        this.render();
        this.log_hook('setup');
    }

    deconstruct() {
        this.log_hook('deconstruct');
    }

    data_updated() {
        this.render();
    }
}


class WidgetApiTestWidget {

    // helper -----------------------------------------------------------------
    render(data) {
        this.rootNode.children[1].innerHTML = JSON.stringify(data);
    }

    log_hook(name) {
        const element = this.lonaWindow.root_node.querySelector(
            '#widget-hooks',
        );

        if(!element) {
            return;
        }

        if(element.innerHTML != '') {
            element.innerHTML = `${element.innerHTML},`;
        }

        element.innerHTML = `${element.innerHTML}${name}`;
    }

    // hooks ------------------------------------------------------------------
    constructor(lonaWindow, rootNode, widgetData) {
        this.lonaWindow = lonaWindow;
        this.rootNode = rootNode;
        this.widgetData = widgetData;

        this.render(this.widgetData.data);
        this.log_hook('constructor');
    }

    destroy() {
        this.log_hook('destroy');
    }

    onDataUpdated(widgetData) {
        this.render(widgetData.data);
    }
}


class HTMLConsoleWidget {
    constructor(lona_window) {
        this.lona_window = lona_window;
    }

    escape_html(html_string) {
        return html_string.replace(
            /&/g, '&amp;',
        ).replace(
            /</g, '&lt;',
        ).replace(
            />/g, '&gt;',
        );
    }

    format_html(html_string) {
        const tab = '    ';
        let result = '';
        let indent= '';

        html_string.split(/>\s*</).forEach(element => {
            if(element.match(/^\/\w/)) {
                indent = indent.substring(tab.length);
            }

            result += `${indent}<${element}>\r\n`;

            if(element.match(/^<?\w[^>]*[^\/]$/)) {
                indent += tab;
            }
        });

        result = result.substring(1, result.length-3);

        return this.escape_html(result);
    }

    render() {
        let formatted_html = this.format_html(this._root_node.innerHTML);

        if(formatted_html == '') {
            formatted_html = '[EMPTY]';
        }

        this.pre.innerHTML = formatted_html;
    }

    setup() {
        this._root_node = document.querySelector(this.data['root_node']);
        this.pre = this.root_node.children[0];

        this.render();
    }

    data_updated() {
        setTimeout(() => {  // FIXME: add description
            this.render();
        }, 0);
    }
}


Lona.register_widget_class(
    'LegacyWidgetApiTestWidget',
    LegacyWidgetApiTestWidget,
);

Lona.register_widget_class('WidgetApiTestWidget', WidgetApiTestWidget);
Lona.register_widget_class('HTMLConsoleWidget', HTMLConsoleWidget);
