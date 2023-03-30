/* MIT License

Copyright (c) 2020 Florian Scherf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

import { Widget } from '../client2/widget.js';
import { Lona } from './lona.js';

const DEFAULT_NODE_NAMESPACE = 'http://www.w3.org/1999/xhtml';


export class LonaDomRenderer {
    constructor(lona_context, lona_window) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;

        this._dom_parser = new DOMParser();
    };

    _parse_html_string(html_string) {
        return this._dom_parser.parseFromString(
            html_string,
            'text/html',
        ).documentElement.textContent;
    }

    // html rendering ---------------------------------------------------------
    _render_node(node_spec) {
        var property_names = ['value', 'checked', 'selected'];

        var node_list = [];
        var node_type = node_spec[0];

        // Node
        if(node_type == Lona.protocol.NODE_TYPE.NODE) {
            var node_id = node_spec[1];
            var node_namespace = node_spec[2] || DEFAULT_NODE_NAMESPACE;
            var node_tag_name = node_spec[3];
            var node_id_list = node_spec[4];
            var node_class_list = node_spec[5];
            var node_style = node_spec[6];
            var node_attributes = node_spec[7];
            var node_child_nodes = node_spec[8];
            var widget_class_name = node_spec[9];
            var widget_data = node_spec[10];

            var node = document.createElementNS(node_namespace, node_tag_name);

            // lona node id
            node.setAttribute('data-lona-node-id', node_id);

            // id list
            if(node_id_list.length > 0) {
                this.lona_window._dom_updater._add_id(node, node_id_list);
            };

            // class list
            if(node_class_list.length > 0) {
                node.classList = node_class_list.join(' ').trim();
            };

            // style
            if(Object.keys(node_style).length > 0) {
                Object.keys(node_style).forEach(key => {
                    node.style.setProperty(key, node_style[key]);
                });
            };

            // attributes
            if(Object.keys(node_attributes).length > 0) {
                Object.keys(node_attributes).forEach(key => {
                    var value = node_attributes[key];

                    // properties
                    if(property_names.indexOf(key) > -1) {
                        if(key != 'value' && node_attributes[key] !== false) {
                            value = true;
                        };

                        node[key] = value;

                    // attributes
                    } else {
                        node.setAttribute(key, node_attributes[key]);

                    };
                });
            };

            // nodes
            node_child_nodes.forEach(sub_node_argspec => {
                var sub_node_list = this._render_node(
                    sub_node_argspec);

                this.lona_window._dom_updater._apply_node_list(
                    node,
                    sub_node_list,
                );
            });

            this.lona_window._nodes[node_id] = node;
            node_list.push(node);

            // widget
            if(widget_class_name != '') {
                if(!(widget_class_name in Lona.widget_classes)) {
                    throw(`RuntimeError: unknown widget name '${widget_class_name}'`);
                }

                const widget = new Widget(
                    this.lona_context,
                    this.lona_window,
                    node,
                    node_id,
                    Lona.widget_classes[widget_class_name],
                    widget_data,
                );

                this.lona_window._widgets[node_id] = widget;
                this.lona_window._widgets_to_setup.splice(0, 0, node_id);
            }

        // TextNode
        } else if(node_type == Lona.protocol.NODE_TYPE.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = this._parse_html_string(node_spec[2]);

            var node = document.createTextNode(node_content);

            this.lona_window._nodes[node_id] = node;
            node_list.push(node);

        // Widget
        } else if(node_type == Lona.protocol.NODE_TYPE.WIDGET) {
            var node_id = node_spec[1];
            var node_widget_class_name = node_spec[2];
            var node_child_nodes = node_spec[3];
            var widget_data = node_spec[4];

            // setup marker
            var start_marker = document.createComment(
                'lona-widget:' + node_id);

            var end_marker = document.createComment(
                'end-lona-widget:' + node_id);

            this.lona_window._widget_marker[node_id] = start_marker;

            node_list.push(start_marker);

            // nodes
            node_child_nodes.forEach(sub_node_argspec => {
                var sub_node_list = this._render_node(
                    sub_node_argspec);

                node_list.push(sub_node_list);
            });

            // append end marker
            node_list.push(end_marker);

            // setup widget
            if(node_widget_class_name in Lona.widget_classes) {
                const widget = new Widget(
                    this.lona_context,
                    this.lona_window,
                    node_list.slice(1, -1).flat(),
                    node_id,
                    Lona.widget_classes[node_widget_class_name],
                    widget_data,
                );

                this.lona_window._widgets[node_id] = widget;
                this.lona_window._widgets_to_setup.splice(0, 0, node_id);
            };
        };

        // patch input events
        node_list.forEach(node => {
            this.lona_window._input_event_handler.patch_input_events(node);
        });

        return node_list;
    };

    _render_nodes(node_specs) {
        // TODO: get rid of this method and move functionality
        // into _render_node()

        var node_list = [];

        for(var index in node_specs) {
            node_list = node_list.concat(this._render_node(node_specs[index]));
        };

        // patch input events
        node_list.forEach(node => {
            this.lona_window._input_event_handler.patch_input_events(node);
        });

        return node_list;
    };
};
