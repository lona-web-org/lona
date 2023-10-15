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

'use strict';

import { Widget } from './widget.js';
import { Lona } from './lona.js';

const SPECIAL_ATTRIBUTE_NAMES = ['id', 'class', 'style', 'data-lona-node-id'];
const PROPERTY_NAMES = ['value', 'checked', 'selected'];
const DEFAULT_NODE_NAMESPACE = 'http://www.w3.org/1999/xhtml';


export class LonaRenderingEngine {
    constructor(lona_context, lona_window, root) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;
        this._root = root;

        this._nodes = new Map();
        this._widgets = new Map();
        this._widgets_to_setup = new Array();
        this._widgets_to_update = new Array();
        this._dom_parser = new DOMParser();
    };

    // helper -----------------------------------------------------------------
    _clear() {
        this._root.innerHTML = '';
        this.lona_window._input_event_handler.reset();
    };

    _add_id(node, id) {
        let id_list = node.id.split(' ');

        id_list = id_list.concat(id);
        node.id = id_list.join(' ').trim();
    };

    _remove_id(node, id) {
        let id_list = node.id.split(' ');

        id_list = id_list.filter(_id => _id != id);
        node.id = id_list.join(' ').trim();
    };

    _get_node(node_id) {
        if(!(this._nodes.has(node_id))) {
            throw(`unknown node id: ${node_id}`);
        }

        return this._nodes.get(node_id);
    };

    _cache_node(node_id, node) {
        if(this._nodes.has(node_id)) {
            throw(`node with id ${node_id} is already cached`);
        }

        this._nodes.set(node_id, node);
    };

    _insert_node(node, node_id, index) {
        const target_node = this._get_node(node_id);

        if(index >= target_node.childNodes.length) {
            target_node.appendChild(node)
        } else {
            target_node.insertBefore(node, target_node.childNodes[index])
        }
    };

    _set_node(node, node_id, index) {
        const target_node = this._get_node(node_id).childNodes[index];

        target_node.replaceWith(node);
    };

    _remove_node(node_id) {
        const node = this._get_node(node_id);

        this._nodes.delete(node_id);
        node.remove();

        this._remove_widget_if_present(node_id);
    };

    _remove_widget_if_present(node_id) {
        if(!(this._widgets.has(node_id))) {
            return;
        }

        const widget = this._widgets.get(node_id);

        // destroy widget
        widget.destroy_widget();

        // remove widget
        this._widgets.delete(node_id);

        // remove widget from _widgets_to_setup
        if(this._widgets_to_setup.indexOf(node_id) > -1) {
            this._widgets_to_setup.splice(
                this._widgets_to_setup.indexOf(node_id), 1);
        };

        // remove widget from _widgets_to_update
        if(this._widgets_to_update.indexOf(node_id) > -1) {
            this._widgets_to_update.splice(
                this._widgets_to_update.indexOf(node_id), 1);
        };
    }

    _clear_node(node_id) {
        const node = this._get_node(node_id);

        node.innerHTML = '';
    };

    _parse_html_string(html_string) {
        return this._dom_parser.parseFromString(
            html_string,
            'text/html',
        ).documentElement.textContent;
    }

    // node cache -------------------------------------------------------------
    _clear_node_cache() {
        // destroy widgets
        this._widgets.forEach(widget => {
            widget.destroy_widget();
        });

        // resetting node state
        this._nodes.clear();
        this._widgets.clear();
        this._widgets_to_setup.length = 0;
        this._widgets_to_update.length = 0;
    };

    _clean_node_cache() {
        this._nodes.forEach((node, node_id) => {
            if(this._root.contains(node)) {
                return;
            }

            this._remove_node(node_id);
            this._remove_widget_if_present(node_id);
        });
    };

    // html rendering ---------------------------------------------------------
    _render_node(node_spec) {
        const node_type = node_spec[0];

        // TODO: remove in 2.0
        if(!(node_type == Lona.protocol.NODE_TYPE.NODE ||
            node_type == Lona.protocol.NODE_TYPE.TEXT_NODE)) {

            throw(`unsupported node type: ${node_type}`);
        };

        // TextNode
        if(node_type == Lona.protocol.NODE_TYPE.TEXT_NODE) {
            const node_id = node_spec[1];
            const node_content = this._parse_html_string(node_spec[2]);

            const node = document.createTextNode(node_content);

            this._cache_node(node_id, node);

            return node;
        };

        // Node
        const node_id = node_spec[1];
        const node_namespace = node_spec[2] || DEFAULT_NODE_NAMESPACE;
        const node_tag_name = node_spec[3];
        const node_id_list = node_spec[4];
        const node_class_list = node_spec[5];
        const node_style = node_spec[6];
        const node_attributes = node_spec[7];
        const node_child_nodes = node_spec[8];
        const widget_class_name = node_spec[9];
        const widget_data = node_spec[10];

        const node = document.createElementNS(node_namespace, node_tag_name);

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
                node.style.setProperty(key, node_style[key]);
            });
        };

        // attributes
        if(Object.keys(node_attributes).length > 0) {
            Object.keys(node_attributes).forEach(key => {
                let value = node_attributes[key];

                // properties
                if(PROPERTY_NAMES.indexOf(key) > -1) {
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
            const child_node = this._render_node(child_node_argspec);

            node.appendChild(child_node);
        });

        this._cache_node(node_id, node);

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

            this._widgets.set(node_id, widget);
            this._widgets_to_setup.splice(0, 0, node_id);
        }

        // patch input events
        this.lona_window._input_event_handler.patch_input_events(node);

        return node;
    };

    // hooks ------------------------------------------------------------------
    _run_widget_hooks() {
        // setup
        this._widgets_to_setup.forEach(node_id => {
            if(!this._widgets.has(node_id)) {
                return;
            }

            const widget = this._widgets.get(node_id);

            widget.initialize_widget();
        });

        // data_updated
        this._widgets_to_update.forEach(node_id => {
            if(!this._widgets.has(node_id)) {
                return;
            }

            const widget = this._widgets.get(node_id);

            widget.run_data_updated_hook();
        });

        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    // patches ----------------------------------------------------------------
    _apply_patch_to_node(patch) {
        const node_id = patch[0];
        const patch_type = patch[1];
        const operation = patch[2];
        const data = patch.splice(3);
        const node = this._get_node(node_id);

        // id_list
        if(patch_type == Lona.protocol.PATCH_TYPE.ID_LIST) {

            // ADD
            if(operation == Lona.protocol.OPERATION.ADD) {
                this._add_id(node, data[0]);

            // RESET
            } else if(operation == Lona.protocol.OPERATION.RESET) {
                node.removeAttribute('id');

                data[0].forEach(id => {
                    this._add_id(node, id);
                });

            // REMOVE
            } else if(operation == Lona.protocol.OPERATION.REMOVE) {
                this._remove_id(node, data[0]);

            // CLEAR
            } else if(operation == Lona.protocol.OPERATION.CLEAR) {
                node.removeAttribute('id');

            };

        // class list
        } else if(patch_type == Lona.protocol.PATCH_TYPE.CLASS_LIST) {

            // ADD
            if(operation == Lona.protocol.OPERATION.ADD) {
                node.classList.add(data[0]);

            // RESET
            } else if(operation == Lona.protocol.OPERATION.RESET) {
                node.classList = data[0].join(' ');

            // REMOVE
            } else if(operation == Lona.protocol.OPERATION.REMOVE) {
                node.classList.remove(data[0]);

            // CLEAR
            } else if(operation == Lona.protocol.OPERATION.CLEAR) {
                node.removeAttribute('class');

            };

        // style
        } else if(patch_type == Lona.protocol.PATCH_TYPE.STYLE) {

            // SET
            if(operation == Lona.protocol.OPERATION.SET) {
                node.style.setProperty(data[0], data[1]);

            // RESET
            } else if(operation == Lona.protocol.OPERATION.RESET) {
                node.removeAttribute('style');

                for(let key in data[0]) {
                    node.style.setProperty(key, data[0][key]);
                };

            // REMOVE
            } else if(operation == Lona.protocol.OPERATION.REMOVE) {
                node.style.setProperty(data[0], '');

            // CLEAR
            } else if(operation == Lona.protocol.OPERATION.CLEAR) {
                node.removeAttribute('style');

            };

        // attributes
        } else if(patch_type == Lona.protocol.PATCH_TYPE.ATTRIBUTES) {

            // SET
            if(operation == Lona.protocol.OPERATION.SET) {
                const name = data[0];
                let value = data[1];

                // properties
                if(PROPERTY_NAMES.indexOf(name) > -1) {
                    if(name != 'value' && value !== false) {
                        value = true;
                    };

                    node[name] = value;

                // attributes
                } else {
                    node.setAttribute(name, value);
                };

            // RESET
            } else if(operation == Lona.protocol.OPERATION.RESET) {
                node.getAttributeNames().forEach(function(name) {
                    if(SPECIAL_ATTRIBUTE_NAMES.indexOf(name) > -1) {
                        return;

                    };

                    node.removeAttribute(name);
                });

                for(let name in data[0]) {
                    let value = data[0][name];

                    // properties
                    if(PROPERTY_NAMES.indexOf(name) > -1) {
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
            } else if(operation == Lona.protocol.OPERATION.REMOVE) {
                const name = data[0];

                // properties
                if(PROPERTY_NAMES.indexOf(name) > -1) {
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
            } else if(operation == Lona.protocol.OPERATION.CLEAR) {
                node.getAttributeNames().forEach(function(name) {
                    if(SPECIAL_ATTRIBUTE_NAMES.indexOf(name) > -1) {
                        return;

                    };

                    node.removeAttribute(name);

                });
            };
        };

        // lona events
        if(patch_type == Lona.protocol.PATCH_TYPE.ATTRIBUTES &&
           data[0] == 'data-lona-events') {

            this.lona_window._input_event_handler.patch_input_events(node);
        };
    };

    _apply_patch_to_child_nodes(patch) {
        const node_id = patch[0];
        const operation = patch[2];
        const data = patch.splice(3);

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            const node = this._render_node(data[1]);

            this._set_node(node, node_id, data[0]);
            this._clean_node_cache();

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            const node = this._get_node(node_id);

            this._clear_node(node_id);
            this._clean_node_cache();

            const child_nodes = data[0].map(node_spec => {
                return this._render_node(node_spec);
            });

            child_nodes.map(child_nodes => {
                node.appendChild(child_nodes);
            });

        // CLEAR
        } else if(operation == Lona.protocol.OPERATION.CLEAR) {
            this._clear_node(node_id);
            this._clean_node_cache();

        // INSERT
        } else if(operation == Lona.protocol.OPERATION.INSERT) {
            const node = this._render_node(data[1]);

            this._insert_node(node, node_id, data[0])

        // REMOVE
        } else if(operation == Lona.protocol.OPERATION.REMOVE) {
            this._remove_node(data[0]);
            this._clean_node_cache();

        };
    };

    _apply_patch_to_widget_data(patch) {
        const node_id = patch[0];
        const operation = patch[2];
        const payload = patch.splice(3);

        const key_path = payload[0];
        const data = payload.splice(1);

        const widget = this._widgets.get(node_id);

        // key path
        let parent_data = undefined;
        let widget_data = widget.raw_widget_data;
        let new_data = undefined;

        key_path.forEach(key => {
            parent_data = widget_data;
            widget_data = widget_data[key];
        });

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            widget_data[data[0]] = data[1];

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            if(parent_data === undefined) {
                widget.raw_widget_data = data[0];

            } else {
                parent_data = data[0];

            };

        // CLEAR
        } else if(operation == Lona.protocol.OPERATION.CLEAR) {
            if(widget_data instanceof Array) {
                new_data = [];

            } else if(widget_data instanceof Object) {
                new_data = {};

            };

            if(parent_data === undefined) {
                widget.raw_widget_data.new_data;

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
        const patch_type = patch[1];

        if(patch_type == Lona.protocol.PATCH_TYPE.WIDGET_DATA) {
            this._apply_patch_to_widget_data(patch);

        } else if(patch_type == Lona.protocol.PATCH_TYPE.NODES) {
            this._apply_patch_to_child_nodes(patch);

        } else {
            this._apply_patch_to_node(patch);
        };
    };

    // public api -------------------------------------------------------------
    show_html(html) {
        const message_type = html[0];
        const data = html[1];

        // HTML
        if (message_type == Lona.protocol.DATA_TYPE.HTML) {
            this._root.innerHTML = data;
            this._clear_node_cache();
            this.lona_window._input_event_handler.patch_input_events_recursively(this._root);

        // HTML tree
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_TREE) {
            this._clear_node_cache();

            const node = this._render_node(data)

            this._clear();
            this._root.appendChild(node);

        // HTML update
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_UPDATE) {
            this._widgets_to_setup = [];
            this._widgets_to_update = [];

            data.forEach(patch => {
                this._apply_patch(patch);
            });
        };

        this._run_widget_hooks();
    };
};
