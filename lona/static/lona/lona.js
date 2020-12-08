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

function JobQueue() {
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


function LonaWindow(lona, root, window_id) {
    this.lona = lona;
    this._root = root;
    this._window_id = window_id;

    this._job_queue = new JobQueue();

    // window state -----------------------------------------------------------
    this._view_stopped = undefined;
    this._url = undefined;
    this._text_nodes = {};
    this._widget_marker = {};

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
            var selector = '[id~=lona-' + node_id + ']';

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
            var selector = '[id~=lona-' + target_node_id + ']';
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
            var selector = '[id~=lona-' + node_id + ']';

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
            var selector = '[id~=lona-' + node_id + ']';
            var node = lona_window._root.querySelector(selector);

            if(!node) {
                return;
            };

            node.innerHTML = '';
            lona_window._clean_node_cache();
        };
    };

    // html rendering ---------------------------------------------------------
    this._render_node = function(node_spec) {
        // TODO: move lona node ids to a custom node attribute to get rid of
        // selectors like [id~=lona-123456789]

        var lona_window = this;
        var node_list = [];
        var node_type = node_spec[0];

        // Node
        if(node_type == Lona.symbols.NodeType.NODE) {
            var node_id = node_spec[1];
            var node_tag_name = node_spec[2];
            var node_id_list = node_spec[3];
            var node_class_list = node_spec[4];
            var node_style = node_spec[5];
            var node_attributes = node_spec[6];
            var node_child_nodes = node_spec[7];

            var node = document.createElement(node_tag_name);

            // lona node id
            lona_window._add_id(node, 'lona-' + node_id);

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
        } else if(node_type == Lona.symbols.NodeType.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = node_spec[2];

            var node = document.createTextNode(node_content);

            lona_window._text_nodes[node_id] = node;
            node_list.push(node);

        // Widget
        } else if(node_type == Lona.symbols.NodeType.WIDGET) {
            var node_id = node_spec[1];
            var node_child_nodes = node_spec[2];

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
            if(operation == Lona.symbols.Operation.SET) {
                var node_list = this._render_node(update[2]);

                this._set_node(node_list, node_id, update[1]);

            // RESET
            } else if(operation == Lona.symbols.Operation.RESET) {
                var node_list = this._render_nodes(update[1]);

                this._clear_node(node_id);
                this._insert_node(node_list, node_id, 0);

            // CLEAR
            } else if(operation == Lona.symbols.Operation.CLEAR) {
                this._clear_node(node_id);

            // INSERT
            } else if(operation == Lona.symbols.Operation.INSERT) {
                var node_list = this._render_node(update[2]);

                this._insert_node(node_list, node_id, update[1])

            // REMOVE
            } else if(operation == Lona.symbols.Operation.REMOVE) {
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

                // nodes
                if(node_updates.length > 0) {
                    lona_window._apply_node_updates(node_id, node_updates);
                };

            // Node
            } else {
                var selector = '[id~=lona-' + node_id + ']';
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
                    if(operation == symbols.Operation.ADD) {
                        lona_window._add_id(node, update[1]);

                    // RESET
                    } else if(operation == symbols.Operation.RESET) {
                        node.removeAttribute('id');

                        lona_window._add_id(node, 'lona-' + node_id)

                        for(var i in update[1]) {
                            lona_window._add_id(update[1][i]);

                        };

                    // REMOVE
                    } else if(operation == symbols.Operation.REMOVE) {
                        lona_window._remove_id(node, update[1]);

                    // CLEAR
                    } else if(operation == symbols.Operation.CLEAR) {
                        node.removeAttribute('id');

                        lona_window._add_id(node, 'lona-' + node_id)

                    };
                };

                // class
                for(var index in class_updates) {
                    var update = class_updates[index];
                    var operation = update[0];

                    // ADD
                    if(operation == symbols.Operation.ADD) {
                        node.classList.add(update[1]);

                    // RESET
                    } else if(operation == symbols.Operation.RESET) {
                        node.classList = update[1].join(' ');

                    // REMOVE
                    } else if(operation == symbols.Operation.REMOVE) {
                        node.classList.remove(update[1]);

                    // CLEAR
                    } else if(operation == symbols.Operation.CLEAR) {
                        node.classList = '';

                    };
                };
                
                // style
                for(var index in style_updates) {
                    var update = style_updates[index];
                    var operation = update[0];

                    // SET
                    if(operation == symbols.Operation.SET) {
                        node.style[update[1]] = update[2];

                    // RESET
                    } else if(operation == symbols.Operation.RESET) {
                        node.removeAttribute('style');

                        for(var key in update[1]) {
                            node.style[key] = update[1][key];
                        };

                    // REMOVE
                    } else if(operation == symbols.Operation.REMOVE) {
                        node.style[update[1]] = '';

                    // CLEAR
                    } else if(operation == symbols.Operation.CLEAR) {
                        node.removeAttribute('style');

                    };
                };

                // attributes
                for(var index in attribute_updates) {
                    var update = attribute_updates[index];
                    var operation = update[0];

                    // SET
                    if(operation == symbols.Operation.SET) {
                        node.setAttribute(update[1], update[2]);

                    // RESET
                    } else if(operation == symbols.Operation.RESET) {
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
                    } else if(operation == symbols.Operation.REMOVE) {
                        node.removeAttribute(update[1]);

                    // CLEAR
                    } else if(operation == symbols.Operation.CLEAR) {
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
        var lona = lona_window.lona;

        lona_window._job_queue.add(function() {
            var message_type = html[0];
            var html_data = html[1];

            // HTML
            if(message_type == Lona.symbols.DataType.HTML) {
                lona_window._root.innerHTML = html_data;
                lona_window._clean_node_cache();

            // HTML tree
            } else if(message_type == Lona.symbols.DataType.HTML_TREE) {
                lona_window._clear_node_cache();

                var node_list = lona_window._render_node(html_data)

                lona_window._clear();
                lona_window._apply_node_list(lona_window._root, node_list);

            // HTML update
            } else if(message_type == Lona.symbols.DataType.HTML_UPDATE) {
                lona_window._apply_update(html_data);

            };

            lona_window._patch_input_events();

        });
    };

    // events -----------------------------------------------------------------
    this._patch_input_events = function() {
        var lona_window = this;
        var lona = lona_window.lona;

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
                    node, Lona.symbols.InputEventType.CLICK, event_data);

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
                    node, Lona.symbols.InputEventType.CHANGE, event_data);

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
                        node, Lona.symbols.InputEventType.SUBMIT, data);

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
        if(message[1] == Lona.symbols.Method.REDIRECT) {
            // TODO: implement loop detection

            if(this.lona.settings.follow_redirects) {
                this.run_view(message[3]);

            } else {
                console.debug(
                    "lona: redirect to '" + message[3] + "' skipped");

            };

        // http redirect
        } else if(message[1] == Lona.symbols.Method.HTTP_REDIRECT) {
            if(this.lona.settings.follow_http_redirects) {
                window.location = message[3];

            } else {
                console.debug(
                    "lona: http redirect to '" + message[3] + "' skipped");

            };

        // data
        } else if(message[1] == Lona.symbols.Method.DATA) {
            var url = message[2];

            if(url != this._url) {
                // this HTML message seems to be related to a previous view

                return;
            };

            var title = message[3];
            var html = message[4];
            var widget_data = message[5];

            if(this.lona.settings.update_title && title) {
                document.title = title;
            };

            if(html) {
                this._show_html(html);
            };

        } else if(message[1] == Lona.symbols.Method.VIEW_STOP) {
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
            Lona.symbols.Method.VIEW,
            url,
            post_data,
        ];

        if(this.lona.settings.update_address_bar) {
            history.pushState({}, '', url);
        };

        if(this.lona.settings.update_title && this.lona.settings.title) {
            document.title = this.lona.settings.title;
        };

        this.lona.send(message);
    };

    this.fire_input_event = function(node, event_type, data) {
        if(data == undefined) {
            data = [];
        };

        if(Array.isArray(data)) {
            data = [data];
        };

        // node info
        var lona_node_id = undefined;
        var node_id_list = node.id.split(' ');

        for(var i=0; i<node_id_list.length; i++) {
            if(node_id_list[i].startsWith('lona-')) {
                lona_node_id = node_id_list[i].split('-')[1];

                break;
            };
        };

        var node_info = [
            lona_node_id,
            node.tagName,
            node.id || '',
            node.classList.value || '',
        ];

        // send event message
        var message = [
            this._window_id,
            Lona.symbols.Method.INPUT_EVENT,
            this._url,
            event_type,
        ].concat(
            data,
        ).concat(
            node_info,
        );

        this.lona.send(message);
    };

    this.setup = function(url) {
        this.run_view(url);
    };
};


function Lona(settings) {
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

    // window -----------------------------------------------------------------
    this.create_window = function(root, url) {
        if(typeof(root) == 'string') {
            root = document.querySelector(root);
        };

        var window_id = Object.keys(this._windows).length + 1;

        this._windows[window_id] = new LonaWindow(this, root, window_id, url);
        this._windows[window_id].setup(url);

        return window_id;
    };

    // websocket messages -----------------------------------------------------
    this.send = function(message) {
        if(typeof(message) != 'string') {
            message = JSON.stringify(message);
        };

        console.debug('lona tx >>', message);

        this._ws.send(message);
    };

    this._run_custom_message_handlers = function(raw_message, json_data) {
        // TODO

    };

    this._handle_raw_websocket_message = function(event) {
        var raw_message = event.data;
        var json_data = undefined;

        console.debug('lona rx <<', raw_message);

        // parse json
        try {
            var json_data = JSON.parse(raw_message);

        } catch {
            return this.lona._run_custom_message_handlers(
                raw_message, json_data);

        };

        // all lona messages are Arrays
        if(!Array.isArray(json_data)) {
            return this.lona._run_custom_message_handlers(
                raw_message, json_data);
        };

        // all lona messages have to start with a window id
        if(!Number.isInteger(json_data[0])) {
            return this.lona._run_custom_message_handlers(
                raw_message, json_data);
        };

        var window_id = json_data[0];

        if(window_id in this.lona._windows) {
            this.lona._windows[window_id].handle_websocket_message(json_data);
        };
    };

    // setup ------------------------------------------------------------------
    this.setup = function() {
        // setup websocket
        var protocol = 'ws://';

        if(window.location.protocol == 'https:') {
            protocol = 'wss://';
        }

        this._ws = new WebSocket(
            protocol + window.location.host + window.location.pathname);

        this._ws.lona = this;
        this._ws.onmessage = this._handle_raw_websocket_message;

        // load initial page
        this._ws.onopen = function(event) {
            var window_id = this.lona.create_window(
                this.lona.settings.target,
                document.location.href,
            );

            // setup pushstate
            if(this.lona.settings.update_address_bar) {
                window.onpopstate = function(event) {
                    this.lona._windows[window_id].run_view(
                        document.location.href);
                };
            };
        };
    };
};
