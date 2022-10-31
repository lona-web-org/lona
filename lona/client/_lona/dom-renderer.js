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

import { LonaWindowShim } from './window-shim.js';
import { Lona } from './lona.js';


export class LonaDomRenderer {
    constructor(lona_context, lona_window) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;
    };

    // html rendering ---------------------------------------------------------
    _render_node(node_spec) {
        var property_names = ['value', 'checked', 'selected'];

        var node_type = node_spec[0];

        // Node
        if(node_type == Lona.protocol.NODE_TYPE.NODE) {
            var node_id = node_spec[1];
            var node_tag_name = node_spec[2];
            var node_id_list = node_spec[3];
            var node_class_list = node_spec[4];
            var node_style = node_spec[5];
            var node_attributes = node_spec[6];
            var node_child_nodes = node_spec[7];
            var widget_class_name = node_spec[8];
            var widget_data = node_spec[9];

            var node = document.createElement(node_tag_name);

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
                    node.style[key] = node_style[key];
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
            node_child_nodes.forEach(child_node_argspec => {
                var child_node = this._render_node(child_node_argspec);

                node.appendChild(child_node);
            });

            this.lona_window._nodes[node_id] = node;

            // widget
            if(widget_class_name != '') {
                if(!(widget_class_name in Lona.widget_classes)) {
                    throw(`RuntimeError: unknown widget name '${widget_class_name}'`);
                }

                var widget_class = Lona.widget_classes[widget_class_name];

                var window_shim = new LonaWindowShim(
                    this.lona_context,
                    this.lona_window,
                    node_id,
                );

                var widget = new widget_class(window_shim);

                this.lona_window._widgets[node_id] = widget;
                this.lona_window._widget_data[node_id] = widget_data;
                this.lona_window._widgets_to_setup.splice(0, 0, node_id);
            }

            // patch input events
            this.lona_window._input_event_handler.patch_input_events(node);

        // TextNode
        } else if(node_type == Lona.protocol.NODE_TYPE.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = node_spec[2];

            var node = document.createTextNode(node_content);

            this.lona_window._nodes[node_id] = node;
        };

        return node;
    };
};
