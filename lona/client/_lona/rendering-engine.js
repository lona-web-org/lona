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


export class LonaRenderingEngine {
    constructor(lona_context, lona_window, root) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;
        this._root = root;

        this._nodes = {};
        this._widget_data = {};
        this._widgets = {};
        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    // helper -----------------------------------------------------------------
    _clear() {
        this._root.innerHTML = '';
        this.lona_window._input_event_handler.reset();
    };

    _add_id(node, id) {
        var id_list = node.id.split(' ');

        id_list = id_list.concat(id);
        node.id = id_list.join(' ').trim();
    };

    _remove_id(node, id) {
        var id_list = node.id.split(' ');

        id_list = id_list.filter(_id => _id != id);
        node.id = id_list.join(' ').trim();
    };

    _get_node(node_id) {
        if(!(node_id in this._nodes)) {
            throw(`unknown node id: ${node_id}`);
        }

        return this._nodes[node_id];
    };

    _insert_node(node, node_id, index) {
        const target_node = this._get_node(node_id);

        if(index >= target_node.children.length) {
            target_node.appendChild(node)
        } else {
            target_node.insertBefore(node, target_node.children[index])
        }
    };

    _set_node(node, node_id, index) {
        const target_node = this._get_node(node_id).children[index];

        target_node.replaceWith(node);
    };

    _remove_node(node_id) {
        const node = this._get_node(node_id);

        delete this._nodes[node_id];
        node.remove();
    };

    _clear_node(node_id) {
        const node = this._get_node(node_id);

        node.innerHTML = '';
    };

    // node cache -------------------------------------------------------------
    _clear_node_cache() {
        // running widget deconstructors
        for(var key in this._widgets) {
            if(this._widgets[key].deconstruct !== undefined) {
                this._widgets[key].deconstruct();
            };
        };

        // resetting node state
        this._nodes = {};
        this._widget_data = {};
        this._widgets = {}
        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    _clean_node_cache() {
        // nodes
        Object.keys(this._nodes).forEach(key => {
            var node = this._get_node(key);

            if(!this._root.contains(node)) {
                this._remove_node(key);
            };
        });

        Object.keys(this._widgets).forEach(key => {
            var node = this._get_node(key);

            // widget_marker
            if(this._root.contains(node)) {
                return;
            };

            // run deconstructor
            if(this._widgets[key].deconstruct !== undefined) {
                this._widgets[key].deconstruct();
            };

            // remove widget
            delete this._widgets[key];

            // remove widget data
            delete this._widget_data[key];

            // remove widget from _widgets_to_setup
            if(this._widgets_to_setup.indexOf(key) > -1) {
                this._widgets_to_setup.splice(
                    this._widgets_to_setup.indexOf(key), 1);
            };

            // remove widget from _widgets_to_update
            if(this._widgets_to_update.indexOf(key) > -1) {
                this._widgets_to_update.splice(
                    this._widgets_to_update.indexOf(key), 1);
            };
        });
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
                this._add_id(node, node_id_list);
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

            this._nodes[node_id] = node;

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

                this._widgets[node_id] = widget;
                this._widget_data[node_id] = widget_data;
                this._widgets_to_setup.splice(0, 0, node_id);
            }

            // patch input events
            this.lona_window._input_event_handler.patch_input_events(node);

        // TextNode
        } else if(node_type == Lona.protocol.NODE_TYPE.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = node_spec[2];

            var node = document.createTextNode(node_content);

            this._nodes[node_id] = node;
        };

        return node;
    };

    // hooks ------------------------------------------------------------------
    _run_widget_hooks() {
        // setup
        this._widgets_to_setup.forEach(node_id => {
            var widget = this._widgets[node_id];
            var widget_data = this._widget_data[node_id];

            widget.data = JSON.parse(JSON.stringify(widget_data));

            if(widget === undefined) {
                return;
            };

            widget.nodes = [this._get_node(node_id)];
            widget.root_node = widget.nodes[0];

            if(widget.setup !== undefined) {
                widget.setup();
            };
        });

        // data_updated
        this._widgets_to_update.forEach(node_id => {
            var widget = this._widgets[node_id];
            var widget_data = this._widget_data[node_id];

            widget.data = JSON.parse(JSON.stringify(widget_data));

            if(widget === undefined) {
                return;
            };

            if(widget.data_updated !== undefined) {
                widget.data_updated();
            };
        });

        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    // patches ----------------------------------------------------------------
    _apply_patch_to_node(patch) {
        var protocol = Lona.protocol;
        var property_names = ['value', 'checked', 'selected'];

        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var data = patch.splice(3);
        var node = this._get_node(node_id);

        // id_list
        if(patch_type == protocol.PATCH_TYPE.ID_LIST) {

            // ADD
            if(operation == protocol.OPERATION.ADD) {
                this._add_id(node, data[0]);

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.removeAttribute('id');

                for(var i in data) {
                    this._add_id(node, data[0]);
                };

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                this._remove_id(node, data[0]);

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.removeAttribute('id');

            };

        // class list
        } else if(patch_type == protocol.PATCH_TYPE.CLASS_LIST) {

            // ADD
            if(operation == protocol.OPERATION.ADD) {
                node.classList.add(data[0]);

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.classList = data[0].join(' ');

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                node.classList.remove(data[0]);

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.removeAttribute('class');

            };

        // style
        } else if(patch_type == protocol.PATCH_TYPE.STYLE) {

            // SET
            if(operation == protocol.OPERATION.SET) {
                node.style[data[0]] = data[1];

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.removeAttribute('style');

                for(var key in data[0]) {
                    node.style[key] = data[0][key];
                };

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                node.style[data[0]] = '';

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.removeAttribute('style');

            };

        // attributes
        } else if(patch_type == protocol.PATCH_TYPE.ATTRIBUTES) {

            // SET
            if(operation == protocol.OPERATION.SET) {
                var name = data[0];
                var value = data[1];

                // properties
                if(property_names.indexOf(name) > -1) {
                    if(name != 'value' && value !== false) {
                        value = true;
                    };

                    node[name] = value;

                // attributes
                } else {
                    node.setAttribute(name, value);
                };

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.getAttributeNames().forEach(function(name) {
                    if(['id', 'class', 'style'].indexOf(name) > -1) {
                        return;

                    };

                    node.removeAttribute(name);
                });

                for(var name in data[0]) {
                    var value = data[0][name];

                    // properties
                    if(property_names.indexOf(name) > -1) {
                        if(name != 'value' && value !== false) {
                            value = true;
                        };

                        node[name] = value;

                    // attributes
                    } else {
                        node.setAttribute(name, value);
                    };
                };

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                var name = data[0];

                // properties
                if(property_names.indexOf(name) > -1) {
                    if(name == 'value') {
                        node[name] = '';

                    } else {
                        node[name] = false;

                    };

                // attributes
                } else {
                    node.removeAttribute(name);
                };

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.getAttributeNames().forEach(function(name) {
                    if(['id', 'class', 'style'].indexOf(name) > -1) {
                        return;

                    };

                    node.removeAttribute(name);

                });
            };
        };

        // lona events
        if(patch_type == protocol.PATCH_TYPE.ATTRIBUTES &&
           data[0] == 'data-lona-events') {

            this.lona_window._input_event_handler.patch_input_events(node);
        };
    };

    _apply_patch_to_child_nodes(patch) {
        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var data = patch.splice(3);

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            var node = this._render_node(data[1]);

            this._set_node(node, node_id, data[0]);

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            const node = this._get_node(node_id);

            const child_nodes = data[0].map(node_spec => {
                return this._render_node(node_spec);
            });

            this._clear_node(node_id);

            child_nodes.map(child_nodes => {
                node.appendChild(child_nodes);
            });

        // CLEAR
        } else if(operation == Lona.protocol.OPERATION.CLEAR) {
            this._clear_node(node_id);

        // INSERT
        } else if(operation == Lona.protocol.OPERATION.INSERT) {
            var node = this._render_node(data[1]);

            this._insert_node(node, node_id, data[0])

        // REMOVE
        } else if(operation == Lona.protocol.OPERATION.REMOVE) {
            this._remove_node(data[0]);

        };
    };

    _apply_patch_to_widget_data(patch) {
        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var payload = patch.splice(3);

        var key_path = payload[0];
        var data = payload.splice(1);

        // key path
        var parent_data = undefined;
        var widget_data = this._widget_data[node_id];

        key_path.forEach(function(key) {
            parent_data = widget_data;
            widget_data = widget_data[key];
        });

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            widget_data[data[0]] = data[1];

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            if(parent_data === undefined) {
                this._widget_data[node_id] = data[0];

            } else {
                parent_data = data[0];

            };

        // CLEAR
        } else if(operation == Lona.protocol.OPERATION.CLEAR) {
            if(widget_data instanceof Array) {
                var new_data = [];

            } else if(widget_data instanceof Object) {
                var new_data = {};

            };

            if(parent_data === undefined) {
                this._widget_data[node_id] = new_data;

            } else {
                parent_data[key_path[key_path.length-1]] = new_data;

            };

        // INSERT
        } else if(operation == Lona.protocol.OPERATION.INSERT) {
            widget_data.splice(data[0], 0, data[1]);

        // REMOVE
        } else if(operation == Lona.protocol.OPERATION.REMOVE) {
            if(widget_data instanceof Array) {
                widget_data.splice(data[0], 1);

            } else if(data instanceof Object) {
                delete widget_data[data[0]];

            };
        };

       this._widgets_to_update.splice(0, 0, node_id);
    };

    _apply_patch(patch) {
        var patch_type = patch[1];

        if(patch_type == Lona.protocol.PATCH_TYPE.NODES) {
            this._apply_patch_to_child_nodes(patch);

        } else {
            this._apply_patch_to_node(patch);
        };
    };

    // public api -------------------------------------------------------------
    show_html(html) {
        var message_type = html[0];
        var data = html[1];

        // HTML
        if (message_type == Lona.protocol.DATA_TYPE.HTML) {
            var selector = 'a,form,[data-lona-events]';

            this._root.innerHTML = data;
            this._clean_node_cache();

            this._root.querySelectorAll(selector).forEach(node => {
                this.lona_window._input_event_handler.patch_input_events(node);
            });

        // HTML tree
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_TREE) {
            this._clear_node_cache();

            var node = this._render_node(data)

            this._clear();
            this._root.appendChild(node);

        // HTML update
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_UPDATE) {
            this._widgets_to_setup = [];
            this._widgets_to_update = [];

            data.forEach(patch => {
                var patch_type = patch[1];

                if(patch_type == Lona.protocol.PATCH_TYPE.WIDGET_DATA) {
                    this._apply_patch_to_widget_data(patch);

                } else {
                    this._apply_patch(patch);

                };

                this._clean_node_cache();
            });
        };

        this._run_widget_hooks();
    };
};
