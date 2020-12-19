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

// Lona namespace -------------------------------------------------------------
var Lona = Object();

Lona.symbols = {};  // this gets overridden by lona-symbols.js
Lona.widget_classes = {};

Lona.register_widget_class = function(widget_name, javascript_class) {
    this.widget_classes[widget_name] = javascript_class;
};

// JobQueue -------------------------------------------------------------------
Lona.JobQueue = function() {
    this._promises = [];

    this._lock = function() {
        var promise_resolve;

        var promise = new Promise(function(resolve, reject) {
            promise_resolve = resolve;
        });

        promise.resolve = promise_resolve;

        var new_array_length = this._promises.push(promise);

        if(new_array_length == 1) {
            promise.resolve();
        };

        return promise;
    };

    this._unlock = function() {
        this._promises.shift();

        if(this._promises.length > 0) {
            this._promises[0].resolve();
        };
    };

    this.add = async function(callback) {
        await this._lock();

        try {
            var promise = callback();

            if(promise instanceof Promise) {
                await promise;
            };

        } finally {
            this._unlock();

        };
    };
};

// Lona Window ----------------------------------------------------------------
Lona.LonaWindow = function(lona_context, root, window_id) {
    this.lona_context = lona_context;
    this._root = root;
    this._window_id = window_id;

    this._job_queue = new Lona.JobQueue();

    // window state -----------------------------------------------------------
    this._view_stopped = undefined;
    this._url = undefined;
    this._text_nodes = {};
    this._widget_marker = {};
    this._widgets = {};
    this._widgets_to_setup = [];
    this._widgets_to_update_nodes = [];
    this._widgets_to_update_data = [];

    // html rendering helper --------------------------------------------------
    this._add_id = function(node, id) {
        var id_list = node.id.split(' ');

        id_list = id_list.concat(id);
        node.id = id_list.join(' ').trim();
    };

    this._remove_id = function(node, id) {
        var id_list = node.id.split(' ');

        id_list.pop(id);
        node.id = id_list.join(' ').trim();
    };

    this._clear = function() {
        this._root.innerHTML = '';
    };

    this._clear_node_cache = function() {
        this._text_nodes = {};
        this._widget_marker = {};
        this._widgets_to_setup = [];
        this._widgets_to_update_nodes = [];
        this._widgets_to_update_data = [];
    };

    this._clean_node_cache = function() {
        var lona_window = this;

        // text nodes
        Object.keys(lona_window._text_nodes).forEach(function(key) {
            var node = lona_window._text_nodes[key];

            if(!lona_window._root.contains(node)) {
                delete lona_window._text_nodes[key];
            };
        });

        // widget marker
        Object.keys(lona_window._widget_marker).forEach(function(key) {
            var node = lona_window._widget_marker[key];

            if(!lona_window._root.contains(node)) {
                delete lona_window._widget_marker[key];
                delete lona_window._widgets[key];
            };
        });
    };

    this._apply_node_list = function(node, node_list) {
        for(var index=0; index<node_list.length; index++) {
            if(node_list[index] instanceof Array) {
                this._apply_node_list(node, node_list[index]);

            } else {
                node.appendChild(node_list[index]);

            };
        };
    };

    this._insert_node = function(node_list, node_id, index) {
        var lona_window = this;
        var target_node;
        var cursor = 0;

        // find target node
        // Widget
        if(node_id in lona_window._widget_marker) {
            var marker = lona_window._widget_marker[node_id];

            target_node = marker.parentElement;

            // find widget start
            while(cursor < target_node.childNodes.length) {
                if(target_node.childNodes[cursor] == marker) {
                    cursor++;

                    break;
                };

                cursor++;
            };

        // Node
        } else {
            var selector = '[lona-node-id=_' + node_id + ']';

            target_node = lona_window._root.querySelector(selector);
        }

        // find start index
        while(index > 0) {
            var _node = target_node.childNodes[cursor];

            // skip widgets
            if((_node.nodeType == Node.COMMENT_NODE) &&
               (_node.textContent.startsWith('lona-widget:'))) {

                while(cursor < target_node.childNodes.length) {
                    cursor++;

                    var _node = target_node.childNodes[cursor];

                    if((_node.nodeType == Node.COMMENT_NODE) &&
                       (_node.textContent.startsWith('end-lona-widget:'))) {

                        break;
                    };

                };
            };

            cursor++;
            index--;
        };

        // apply node list
        for(var i=0; i<node_list.length; i++) {
            var new_node = node_list[i];

            if(target_node.childNodes.length == 0) {
                target_node.appendChild(new_node);

            } else {
                target_node.insertBefore(
                    new_node, target_node.childNodes[cursor + i]);
            };
        };
    };

    this._set_node = function(node_list, target_node_id, index) {
        var lona_window = this;
        var target_node;
        var cursor = 0;

        // Widget
        if(target_node_id in lona_window._widget_marker) {
            var marker = lona_window._widget_marker[target_node_id];
            var target_node = marker.parentElement;
            var end_marker_text = 'end-lona-widget:' + target_node_id;

            // find marker
            while(cursor < target_node.childNodes.length) {
                if(target_node.childNodes[cursor] == marker) {
                    cursor++;

                    break;
                };

                cursor++;
            };

        // Node
        } else {
            var selector = '[lona-node-id=_' + target_node_id + ']';
            var target_node = lona_window._root.querySelector(selector);

            if(!target_node) {
                return;
            };

        };

        // find start index
        while(index > 0) {
            var _node = target_node.childNodes[cursor];

            // skip widgets
            if((_node.nodeType == Node.COMMENT_NODE) &&
               (_node.textContent.startsWith('lona-widget:'))) {

                while(cursor < target_node.childNodes.length) {
                    cursor++;

                    var _node = target_node.childNodes[cursor];

                    if((_node.nodeType == Node.COMMENT_NODE) &&
                       (_node.textContent.startsWith('end-lona-widget:'))) {

                        break;
                    };

                };
            };

            cursor++;
            index--;
        };

        // replace node
        var node = target_node.childNodes[cursor];

        // Widget
        if((node.nodeType == Node.COMMENT_NODE) &&
           (node.textContent.startsWith('lona-widget:'))) {

            var widget_id = node.textContent.split(':')[1];
            var end_marker_text = 'end-lona-widget:' + widget_id;

            while(target_node.childNodes.length > 0) {
                var _node = target_node.childNodes[cursor];

                _node.remove();

                if((_node.nodeType == Node.COMMENT_NODE) &&
                   (_node.textContent == end_marker_text)) {

                    break;
                };
            };

        // Node
        } else {
            node.remove();

        };

        // apply node list
        for(var i=0; i<node_list.length; i++) {
            var new_node = node_list[i];

            if(target_node.childNodes.length == 0) {
                target_node.appendChild(new_node);

            } else {
                target_node.insertBefore(
                    new_node, target_node.childNodes[cursor + i]);
            };
        };
    };

    this._remove_node = function(node_id) {
        var lona_window = this;

        // TextNode
        if(node_id in lona_window._text_nodes) {
            lona_window._text_nodes[node_id].remove();

            delete lona_window._text_nodes[node_id];

        // Widget
        } else if(node_id in lona_window._widget_marker) {
            var marker = lona_window._widget_marker[node_id];
            var parent_element = marker.parentElement;
            var end_marker_text = 'end-lona-widget:' + node_id;
            var index = 0;

            while(index < parent_element.childNodes.length) {
                if(parent_element.childNodes[index] == marker) {
                    break;
                };

                index++;
            };

            while(index < parent_element.childNodes.length) {
                var node = parent_element.childNodes[index];

                if((node.nodeType == Node.COMMENT_NODE) &&
                   (node.textContent == end_marker_text)) {

                    node.remove();

                    break;
                };

                node.remove();
            };

            lona_window._clean_node_cache();

        // Node
        } else {
            var selector = '[lona-node-id=_' + node_id + ']';

            node = lona_window._root.querySelector(selector);

            if(node) {
                node.remove();
                lona_window._clean_node_cache();
            };
        };
    };

    this._clear_node = function(node_id) {
        var lona_window = this;

        // Widget
        if(node_id in lona_window._widget_marker) {
            var marker = lona_window._widget_marker[node_id];
            var child_nodes = marker.parentElement.childNodes;
            var end_marker_text = 'end-lona-widget:' + node_id;
            var index = 0;

            while(index < child_nodes.length) {
                if(child_nodes[index] == marker) {
                    break;
                };

                index++;
            };

            index++;

            while(!((child_nodes[index].nodeType == Node.COMMENT_NODE) &&
                    (child_nodes[index].textContent == end_marker_text))) {

                child_nodes[index].remove();
            };

            lona_window._clean_node_cache();

        // Node
        } else {
            var selector = '[lona-node-id=_' + node_id + ']';
            var node = lona_window._root.querySelector(selector);

            if(!node) {
                return;
            };

            node.innerHTML = '';
            lona_window._clean_node_cache();
        };
    };

    // widget helper ----------------------------------------------------------
    this._get_widget_nodes = function(node_id) {
        var lona_window = this;
        var node_list = [];
        var widget_marker = lona_window._widget_marker[node_id];
        var end_marker_text = 'end-lona-widget:' + node_id;
        var cursor = 0;

        // find start marker
        var parent_child_nodes = widget_marker.parentElement.childNodes;

        while(cursor < parent_child_nodes.length) {
            if(parent_child_nodes[cursor] == widget_marker) {
                break;
            };

            cursor++;
        };

        cursor++;

        // find end marker
        while(cursor < parent_child_nodes.length) {
            var node = parent_child_nodes[cursor];

            if((node.nodeType == Node.COMMENT_NODE) &&
               (node.textContent.startsWith(end_marker_text))) {

                break;
            };

            node_list.push(node);
            cursor++;
        };

        return node_list;
    };

    this._apply_widget_data_update = function(widget, updates) {
        for(var index in updates) {
            var update = updates[index];
            var key_path = update[0];
            var operation = update[1];

            // key path
            var parent_data = undefined;
            var data = widget.data;

            key_path.forEach(function(key) {
                parent_data = data;
                data = data[key];
            });

            // SET
            if(operation == Lona.symbols.OPERATION.SET) {
                data[update[2]] = update[3];

            // RESET
            } else if(operation == Lona.symbols.OPERATION.RESET) {
                if(parent_data === undefined) {
                    widget.data = update[2];

                } else {
                    parent_data = update[2];

                };

            // CLEAR
            } else if(operation == Lona.symbols.OPERATION.CLEAR) {
                if(data instanceof Array) {
                    var new_data = [];

                } else if(data instanceof Object) {
                    var new_data = {};

                };

                if(parent_data === undefined) {
                    widget.data = new_data;

                } else {
                    parent_data[key_path[key_path.length-1]] = new_data;

                };

            // INSERT
            } else if(operation == Lona.symbols.OPERATION.INSERT) {
                data.splice(update[2], 0, update[3]);

            // REMOVE
            } else if(operation == Lona.symbols.OPERATION.REMOVE) {
                if(data instanceof Array) {
                    data.splice(update[2], 1);

                } else if(data instanceof Object) {
                    delete data[update[2]];

                };
            };
        };
    };

    this._run_widget_hooks = function() {
        var lona_window = this;

        // setup
        lona_window._widgets_to_setup.forEach(function(node_id) {
            var widget = lona_window._widgets[node_id];

            lona_window._widgets_to_setup.shift();

            if(widget === undefined) {
                return;
            };

            try {
                widget.nodes = lona_window._get_widget_nodes(node_id);

                if(widget.setup !== undefined) {
                    widget.setup();
                };

            } finally {};

        });

        // nodes_updated
        lona_window._widgets_to_update_nodes.forEach(function(node_id) {
            var widget = lona_window._widgets[node_id];

            lona_window._widgets_to_update_nodes.shift();

            if(widget === undefined) {
                return;
            };

            try {
                widget.nodes = lona_window._get_widget_nodes(node_id);

                if(widget.nodes_updated !== undefined) {
                    widget.nodes_updated();
                };

            } finally {};
        });

        // data_updated
        lona_window._widgets_to_update_data.forEach(function(node_id) {
            var widget = lona_window._widgets[node_id];

            lona_window._widgets_to_update_data.shift();

            if(widget === undefined) {
                return;
            };

            try {
                if(widget.data_updated !== undefined) {
                    widget.data_updated();
                };

            } finally {};
        });
    };

    // html rendering ---------------------------------------------------------
    this._render_node = function(node_spec) {
        var lona_window = this;
        var lona_context = this.lona_context;
        var node_list = [];
        var node_type = node_spec[0];

        // Node
        if(node_type == Lona.symbols.NODE_TYPE.NODE) {
            var node_id = node_spec[1];
            var node_tag_name = node_spec[2];
            var node_id_list = node_spec[3];
            var node_class_list = node_spec[4];
            var node_style = node_spec[5];
            var node_attributes = node_spec[6];
            var node_child_nodes = node_spec[7];

            var node = document.createElement(node_tag_name);

            // lona node id
            node.setAttribute('lona-node-id', '_' + node_id);

            // id list
            if(node_id_list.length > 0) {
                lona_window._add_id(node, node_id_list);
            };

            // class list
            if(node_class_list.length > 0) {
                node.classList = node_class_list.join(' ').trim();
            };

            // style
            if(Object.keys(node_style).length > 0) {
                Object.keys(node_style).forEach(function(key) {
                    node.style[key] = node_style[key];
                });
            };

            // attributes
            if(Object.keys(node_attributes).length > 0) {
                Object.keys(node_attributes).forEach(function(key) {
                    node.setAttribute(key, node_attributes[key]);
                });
            };

            // nodes
            node_child_nodes.forEach(function(sub_node_argspec) {
                var sub_node_list = lona_window._render_node(
                    sub_node_argspec);

                lona_window._apply_node_list(node, sub_node_list);
            });

            node_list.push(node);

        // TextNode
        } else if(node_type == Lona.symbols.NODE_TYPE.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = node_spec[2];

            var node = document.createTextNode(node_content);

            lona_window._text_nodes[node_id] = node;
            node_list.push(node);

        // Widget
        } else if(node_type == Lona.symbols.NODE_TYPE.WIDGET) {
            var node_id = node_spec[1];
            var node_widget_class_name = node_spec[2];
            var node_child_nodes = node_spec[3];
            var widget_data = node_spec[4];

            // setup marker
            var start_marker = document.createComment(
                'lona-widget:' + node_id);

            var end_marker = document.createComment(
                'end-lona-widget:' + node_id);

            lona_window._widget_marker[node_id] = start_marker;

            node_list.push(start_marker);

            // nodes
            node_child_nodes.forEach(function(sub_node_argspec) {
                var sub_node_list = lona_window._render_node(
                    sub_node_argspec);

                node_list.push(sub_node_list);
            });

            // append end marker
            node_list.push(end_marker);

            // setup widget
            if(node_widget_class_name in Lona.widget_classes) {
                widget_class = Lona.widget_classes[node_widget_class_name];

                var widget = new widget_class(lona_window);

                widget.data = widget_data;

                lona_window._widgets[node_id] = widget;
                lona_window._widgets_to_setup.splice(0, 0, node_id);
            };
        };

        return node_list;
    };

    this._render_nodes = function(node_specs) {
        // TODO: get rid of this method and move functionality
        // into _render_node()

        var node_list = [];

        for(var index in node_specs) {
            node_list = node_list.concat(this._render_node(node_specs[index]));
        };

        return node_list;
    };

    this._apply_node_updates = function(node_id, updates) {
        for(var i in updates) {
            var update = updates[i];
            var operation = update[0];

            // SET
            if(operation == Lona.symbols.OPERATION.SET) {
                var node_list = this._render_node(update[2]);

                this._set_node(node_list, node_id, update[1]);

            // RESET
            } else if(operation == Lona.symbols.OPERATION.RESET) {
                var node_list = this._render_nodes(update[1]);

                this._clear_node(node_id);
                this._insert_node(node_list, node_id, 0);

            // CLEAR
            } else if(operation == Lona.symbols.OPERATION.CLEAR) {
                this._clear_node(node_id);

            // INSERT
            } else if(operation == Lona.symbols.OPERATION.INSERT) {
                var node_list = this._render_node(update[2]);

                this._insert_node(node_list, node_id, update[1])

            // REMOVE
            } else if(operation == Lona.symbols.OPERATION.REMOVE) {
                this._remove_node(update[1]);

            };
        };
    };

    this._apply_update = function(html_data) {
        var lona_window = this;
        var symbols = Lona.symbols;

        for(var index in html_data) {
            var update = html_data[index];
            var node_id = update[0];

            // Widget
            if(node_id in this._widget_marker) {
                var node_updates = update[1];
                var data_updates = update[2];

                // nodes
                if(node_updates.length > 0) {
                    lona_window._apply_node_updates(node_id, node_updates);
                    lona_window._widgets_to_update_nodes.push(node_id);
                };

                // data
                if(data_updates.length > 0) {
                    this._apply_widget_data_update(
                        this._widgets[node_id], data_updates);

                    lona_window._widgets_to_update_data.splice(0, 0, node_id);
                };

            // Node
            } else {
                var selector = '[lona-node-id=_' + node_id + ']';
                var node = lona_window._root.querySelector(selector);

                if(!node) {
                    continue;
                };

                var id_updates = update[1];
                var class_updates = update[2];
                var style_updates = update[3];
                var attribute_updates = update[4];
                var node_updates = update[5];

                // id
                for(var index in id_updates) {
                    var update = id_updates[index];
                    var operation = update[0];

                    // ADD
                    if(operation == symbols.OPERATION.ADD) {
                        lona_window._add_id(node, update[1]);

                    // RESET
                    } else if(operation == symbols.OPERATION.RESET) {
                        node.removeAttribute('id');

                        lona_window._add_id(node, 'lona-' + node_id)

                        for(var i in update[1]) {
                            lona_window._add_id(update[1][i]);

                        };

                    // REMOVE
                    } else if(operation == symbols.OPERATION.REMOVE) {
                        lona_window._remove_id(node, update[1]);

                    // CLEAR
                    } else if(operation == symbols.OPERATION.CLEAR) {
                        node.removeAttribute('id');

                        lona_window._add_id(node, 'lona-' + node_id)

                    };
                };

                // class
                for(var index in class_updates) {
                    var update = class_updates[index];
                    var operation = update[0];

                    // ADD
                    if(operation == symbols.OPERATION.ADD) {
                        node.classList.add(update[1]);

                    // RESET
                    } else if(operation == symbols.OPERATION.RESET) {
                        node.classList = update[1].join(' ');

                    // REMOVE
                    } else if(operation == symbols.OPERATION.REMOVE) {
                        node.classList.remove(update[1]);

                    // CLEAR
                    } else if(operation == symbols.OPERATION.CLEAR) {
                        node.classList = '';

                    };
                };
                
                // style
                for(var index in style_updates) {
                    var update = style_updates[index];
                    var operation = update[0];

                    // SET
                    if(operation == symbols.OPERATION.SET) {
                        node.style[update[1]] = update[2];

                    // RESET
                    } else if(operation == symbols.OPERATION.RESET) {
                        node.removeAttribute('style');

                        for(var key in update[1]) {
                            node.style[key] = update[1][key];
                        };

                    // REMOVE
                    } else if(operation == symbols.OPERATION.REMOVE) {
                        node.style[update[1]] = '';

                    // CLEAR
                    } else if(operation == symbols.OPERATION.CLEAR) {
                        node.removeAttribute('style');

                    };
                };

                // attributes
                for(var index in attribute_updates) {
                    var update = attribute_updates[index];
                    var operation = update[0];

                    // SET
                    if(operation == symbols.OPERATION.SET) {
                        node.setAttribute(update[1], update[2]);

                    // RESET
                    } else if(operation == symbols.OPERATION.RESET) {
                        node.getAttributeNames().forEach(function(name) {
                            if(['id', 'class', 'style'].indexOf(name) > -1) {
                                return;

                            };

                            node.removeAttribute(name);

                        });

                        for(var name in update[1]) {
                            node.setAttribute(name, update[1][name]);
                        };

                    // REMOVE
                    } else if(operation == symbols.OPERATION.REMOVE) {
                        node.removeAttribute(update[1]);

                    // CLEAR
                    } else if(operation == symbols.OPERATION.CLEAR) {
                        node.getAttributeNames().forEach(function(name) {
                            if(['id', 'class', 'style'].indexOf(name) > -1) {
                                return;

                            };

                            node.removeAttribute(name);

                        });
                    };
                };

                // nodes
                if(node_updates.length > 0) {
                    lona_window._apply_node_updates(node_id, node_updates);
                };

            };
        };
    };

    this._show_html = function(html) {
        var lona_window = this;
        var lona_context = lona_window.lona_context;

        lona_window._job_queue.add(function() {
            var message_type = html[0];
            var data = html[1];

            // HTML
            if(message_type == Lona.symbols.DATA_TYPE.HTML) {
                lona_window._root.innerHTML = data;
                lona_window._clean_node_cache();

            // HTML tree
            } else if(message_type == Lona.symbols.DATA_TYPE.HTML_TREE) {
                lona_window._clear_node_cache();

                var node_list = lona_window._render_node(data)

                lona_window._clear();
                lona_window._apply_node_list(lona_window._root, node_list);

            // HTML update
            } else if(message_type == Lona.symbols.DATA_TYPE.HTML_UPDATE) {
                var html_data = data[0];
                var changed_widgets = data[1];

                lona_window._widgets_to_setup = [];
                lona_window._widgets_to_update_nodes = changed_widgets;
                lona_window._widgets_to_update_data = [];

                lona_window._apply_update(html_data);
            };

            lona_window._run_widget_hooks();
            lona_window._patch_input_events();

        });
    };

    // events -----------------------------------------------------------------
    this._patch_input_events = function() {
        var lona_window = this;
        var lona_context = lona_window.lona_context;

        // links
        var selector = 'a:not(.lona-clickable):not(.lona-ignore)';

        this._root.querySelectorAll(selector).forEach(function(node) {
            node.onclick = function(event) {
                event.preventDefault();

                var element = event.target || event.srcElement;

                lona_window.run_view(element.href);

                return false;
            };
        });

        // click events
        var selector = '.lona-clickable:not(.lona-ignore)';

        this._root.querySelectorAll(selector).forEach(function(node) {
            node.onclick = function(event) {
                event.preventDefault();

                var node = event.target || event.srcElement;

                var event_data = {
                    alt_key: event.altKey,
                    shift_key: event.shiftKey,
                    meta_key: event.metaKey,
                    ctrl_key: event.ctrlKey,
                    node_width: node.offsetWidth,
                    node_height: node.offsetHeight,
                    x: event.offsetX,
                    y: event.offsetY,
                };

                lona_window.fire_input_event(
                    node, Lona.symbols.INPUT_EVENT_TYPE.CLICK, event_data);

                return false;
            };
        });

        // change events
        var selector = '.lona-changeable:not(.lona-ignore)';

        this._root.querySelectorAll(selector).forEach(function(node) {
            node.onchange = function(event) {
                event.preventDefault();

                var node = event.target || event.srcElement;
                var event_data = node.value;

                if(node.getAttribute('type') == 'checkbox') {
                    event_data = node.checked;
                };

                lona_window.fire_input_event(
                    node, Lona.symbols.INPUT_EVENT_TYPE.CHANGE, event_data);

                return false;
            };
        });

        // forms
        var selector = 'form:not(.lona-ignore)';

        this._root.querySelectorAll(selector).forEach(function(node) {
            node.onsubmit = function(event) {
                event.preventDefault();

                // find muliple selects
                // FIXME: why does this not work with plain FormData?
                var multi_selects = {};

                this.querySelectorAll('select[multiple]').forEach(
                    function(select_node) {
                        multi_selects[select_node.name] = [];

                        select_node.querySelectorAll('option').forEach(
                            function(option_node) {
                                if(!option_node.selected) {
                                    return;
                                };

                                multi_selects[select_node.name].push(
                                    option_node.value);
                            }
                        );
                    }
                );

                // generate form data
                var form_data = new FormData(this);

                if(!lona_window._view_stopped) {
                    var data = {};

                    for(let [key, value] of form_data.entries()) {
                        if(key in multi_selects) {
                            data[key] = multi_selects[key];

                        } else {
                            data[key] = value;

                        };
                    }

                    lona_window.fire_input_event(
                        node, Lona.symbols.INPUT_EVENT_TYPE.SUBMIT, data);

                } else {
                    // "traditional" form submit
                    // this is implemented by invoking Method.VIEW with
                    // post_data set instead of an input event

                    var method = (this.method || 'get').toLowerCase();
                    var action = this.action || window.location.href;

                    if(method == 'get') {
                        var url = new URL(action);
                        var href = url.origin + url.pathname;

                        var query = new URLSearchParams(form_data).toString();

                        if(query) {
                            href += '?' + query;
                        };

                        lona_window.run_view(href);

                    } else if(method == 'post') {
                        var post_data = {};

                        for(let [key, value] of form_data.entries()) {
                            post_data[key] = value;
                        }

                        lona_window.run_view(action, post_data);
                    };
                };

                return false;
            };
        });
    };

    // public api -------------------------------------------------------------
    this.handle_websocket_message = function(message) {
        // redirect
        if(message[1] == Lona.symbols.METHOD.REDIRECT) {
            // TODO: implement loop detection

            if(this.lona_context.settings.follow_redirects) {
                this.run_view(message[3]);

            } else {
                console.debug(
                    "lona: redirect to '" + message[3] + "' skipped");

            };

        // http redirect
        } else if(message[1] == Lona.symbols.METHOD.HTTP_REDIRECT) {
            if(this.lona_context.settings.follow_http_redirects) {
                window.location = message[3];

            } else {
                console.debug(
                    "lona: http redirect to '" + message[3] + "' skipped");

            };

        // data
        } else if(message[1] == Lona.symbols.METHOD.DATA) {
            var url = message[2];

            if(url != this._url) {
                // this HTML message seems to be related to a previous view

                return;
            };

            var title = message[3];
            var html = message[4];
            var widget_data = message[5];

            if(this.lona_context.settings.update_title && title) {
                document.title = title;
            };

            if(html) {
                this._show_html(html);
            };

        } else if(message[1] == Lona.symbols.METHOD.VIEW_STOP) {
            this._view_stopped = true;

        };
    };

    this.run_view = function(url, post_data) {
        // Save the requested url to only show HTML messages that are related
        // to this request.
        // This prevents glitches when switching urls fast.
        this._url = url;
        this._view_stopped = false;

        var message = [
            this._window_id,
            Lona.symbols.METHOD.VIEW,
            url,
            post_data,
        ];

        if(this.lona_context.settings.update_address_bar) {
            history.pushState({}, '', url);
        };

        if(this.lona_context.settings.update_title && this.lona_context.settings.title) {
            document.title = this.lona_context.settings.title;
        };

        this.lona_context.send(message);
    };

    this.fire_input_event = function(node, event_type, data) {
        if(data == undefined) {
            data = [];
        };

        if(Array.isArray(data)) {
            data = [data];
        };

        // node info
        var lona_node_id = node.getAttribute('lona-node-id');

        if(lona_node_id) {
            lona_node_id = lona_node_id.substr(1);
        }

        var node_info = [
            lona_node_id,
            node.tagName,
            node.id || '',
            node.classList.value || '',
        ];

        // send event message
        var message = [
            this._window_id,
            Lona.symbols.METHOD.INPUT_EVENT,
            this._url,
            event_type,
        ].concat(
            data,
        ).concat(
            node_info,
        );

        this.lona_context.send(message);
    };

    this.setup = function(url) {
        this.run_view(url);
    };
};

// Lona Context ---------------------------------------------------------------
Lona.LonaContext = function(settings) {
    // settings ---------------------------------------------------------------
    this.settings = settings || {};
    this.settings.target = this.settings.target || '#lona';
    this.settings.title = this.settings.title || '';

    if(typeof(this.settings.update_address_bar) == 'undefined') {
        this.settings.update_address_bar = true;
    };

    if(typeof(this.settings.update_title) == 'undefined') {
        this.settings.update_title = true;
    };

    if(typeof(this.settings.follow_redirects) == 'undefined') {
        this.settings.follow_redirects = true;
    };

    if(typeof(this.settings.follow_http_redirects) == 'undefined') {
        this.settings.follow_http_redirects = true;
    };

    // state ------------------------------------------------------------------
    this._windows = {};
    this._connect_hooks = [];
    this._disconnect_hooks = [];
    this._message_handler = [];

    // window -----------------------------------------------------------------
    this.create_window = function(root, url) {
        if(typeof(root) == 'string') {
            root = document.querySelector(root);
        };

        var window_id = Object.keys(this._windows).length + 1;

        this._windows[window_id] = new Lona.LonaWindow(
            this, root, window_id, url);

        this._windows[window_id].setup(url);

        return window_id;
    };

    // hooks ------------------------------------------------------------------
    this.add_connect_hook = function(hook) {
        this._connect_hooks.push(hook);
    };

    this.add_disconnect_hook = function(hook) {
        this._disconnect_hooks.push(hook);
    };

    this.add_message_handler = function(handler) {
        this._message_handler.push(handler);
    };

    this._run_connect_hooks = function(event) {
        for(var i in this._connect_hooks) {
            var hook = this._connect_hooks[i];

            try {
                hook(this, event);

            } finally {};
        };
    };

    this._run_disconnect_hooks = function(event) {
        for(var i in this._disconnect_hooks) {
            var hook = this._disconnect_hooks[i];

            try {
                hook(this, event);

            } finally {};
        };
    };

    this._run_message_handler = function(raw_message, json_data) {
        message = {
            raw_message: raw_message,
            json_data: json_data,
        };

        for(var i in this._message_handler) {
            var message_handler = this._message_handler[i];

            try {
                var return_value = message_handler(this, message);

                if(!return_value) {
                    return;
                };

            } finally {};
        };
    };

    // websocket messages -----------------------------------------------------
    this.send = function(message) {
        if(typeof(message) != 'string') {
            message = JSON.stringify(message);
        };

        console.debug('lona tx >>', message);

        this._ws.send(message);
    };

    this._handle_raw_websocket_message = function(event) {
        var raw_message = event.data;
        var json_data = undefined;

        console.debug('lona rx <<', raw_message);

        // parse json
        try {
            var json_data = JSON.parse(raw_message);

        } catch {
            return this.lona_context._run_message_handler(
                raw_message, json_data);

        };

        // all lona messages are Arrays
        if(!Array.isArray(json_data)) {
            return this.lona_context._run_message_handler(
                raw_message, json_data);
        };

        // all lona messages have to start with a window id
        if(!Number.isInteger(json_data[0])) {
            return this.lona_context._run_message_handler(
                raw_message, json_data);
        };

        var window_id = json_data[0];

        if(window_id in this.lona_context._windows) {
            let lona_window = this.lona_context._windows[window_id];

            lona_window.handle_websocket_message(json_data);
        };
    };

    // setup ------------------------------------------------------------------
    this.reconnect = function() {
        // state
        this._windows = {};

        // setup websocket
        var protocol = 'ws://';

        if(window.location.protocol == 'https:') {
            protocol = 'wss://';
        }

        this._ws = new WebSocket(
            protocol + window.location.host + window.location.pathname);

        this._ws.lona_context = this;
        this._ws.onmessage = this._handle_raw_websocket_message;

        // onopen
        this._ws.onopen = function(event) {
            var lona_context = this.lona_context;

            // load initial page
            var window_id = this.lona_context.create_window(
                lona_context.settings.target,
                document.location.href,
            );

            // setup pushstate
            if(this.lona_context.settings.update_address_bar) {
                window.onpopstate = function(event) {
                    lona_context._windows[window_id].run_view(
                        document.location.href);
                };
            };

            lona_context._run_connect_hooks(event);
        };

        // onclose
        this._ws.onclose = function(event) {
            var lona_context = this.lona_context;

            lona_context._run_disconnect_hooks(event);
        };
    };

    this.setup = function() {
        this.reconnect();
    };
};
