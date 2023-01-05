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


Lona.register_widget_class('WidgetDataTestWidget', WidgetDataTestWidget);
Lona.register_widget_class('HTMLConsoleWidget', HTMLConsoleWidget);
