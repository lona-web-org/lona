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

import { Lona } from './lona.js';


export class LonaDomUpdater {
    constructor(lona_context, lona_window) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;
    };

    // helper -----------------------------------------------------------------
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
        return this.lona_window._nodes[node_id];
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

        node.remove();
    };

    _clear_node(node_id) {
        const node = this._get_node(node_id);

        node.innerHTML = '';
    };

    // patches ----------------------------------------------------------------
    _apply_patch_to_node(patch) {
        var protocol = Lona.protocol;
        var property_names = ['value', 'checked', 'selected'];

        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var data = patch.splice(3);
        var node = this.lona_window._nodes[node_id];

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
                    if(['id', 'class', 'style', 'data-lona-node-id'].indexOf(name) > -1) {
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
                    if(['id', 'class', 'style', 'data-lona-node-id'].indexOf(name) > -1) {
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

        var dom_renderer = this.lona_window._dom_renderer;

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            var node = dom_renderer._render_node(data[1]);

            this._set_node(node, node_id, data[0]);

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            const node = this._get_node(node_id);

            const child_nodes = data[0].map(node_spec => {
                return dom_renderer._render_node(node_spec);
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
            var node = dom_renderer._render_node(data[1]);

            this._insert_node(node, node_id, data[0])

        // REMOVE
        } else if(operation == Lona.protocol.OPERATION.REMOVE) {
            this._remove_node(data[0]);

        };
    };

    _apply_patch(patch) {
        var patch_type = patch[1];

        if(patch_type == Lona.protocol.PATCH_TYPE.NODES) {
            this._apply_patch_to_child_nodes(patch);

        } else {
            this._apply_patch_to_node(patch);
        };
    };
};
