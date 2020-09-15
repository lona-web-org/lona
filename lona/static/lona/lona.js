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

function Lona(settings) {
    // settings ---------------------------------------------------------------
    this.settings = settings || {};
    this.settings.target = this.settings.target || '#lona';

    if(typeof(this.settings.push_state) == 'undefined') {
        this.settings.push_state = true;
    };

    if(typeof(this.settings.follow_redirects) == 'undefined') {
        this.settings.follow_redirects = true;
    };

    if(typeof(this.settings.follow_http_redirects) == 'undefined') {
        this.settings.follow_http_redirects = true;
    };

    // state ------------------------------------------------------------------
    this.widget_handler = {};

    // handle websocket messages ----------------------------------------------
    this.METHOD = {
        VIEW:                101,
        INPUT_EVENT:         102,
        REDIRECT:            201,
        HTTP_REDIRECT:       202,
        HTML:                203,
    };

    this.INPUT_EVENT_TYPE = {
        CLICK:               301,
        CHANGE:              302,
        SUBMIT:              303,
        CUSTOM:              304,
    };

    this._run_custom_message_handlers = function(raw_message, json_data) {
        // TODO
    };

    this._onmessage = function(event) {
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

        // redirect
        if(json_data[1] == this.lona.METHOD.REDIRECT) {
            // TODO: implement loop detection

            if(this.lona.settings.follow_redirects) {
                this.lona.run_view(json_data[3]);

            } else {
                console.debug(
                    "lona: redirect to '" + json_data[3] + "' skipped");

            };

        // http redirect
        } else if(json_data[1] == this.lona.METHOD.HTTP_REDIRECT) {
            if(this.lona.settings.follow_http_redirects) {
                window.location = json_data[3];

            } else {
                console.debug(
                    "lona: http redirect to '" + json_data[3] + "' skipped");

            };

        // html
        } else if(json_data[1] == this.lona.METHOD.HTML) {
            var url = json_data[2];

            if(url != this.lona.url) {
                // this HTML message seems to be related to a previous view

                return;
            };

            // TODO: title
            history.pushState({}, '', url);

            var html = json_data[3];
            var patch_input_events = json_data[4];

            this.lona._show_html(html, patch_input_events);

        }

        // message is no lona message
        return this.lona._run_custom_message_handlers(
            raw_message, json_data);
    };

    // HTML node handling -----------------------------------------------------
    this._clear = function() {
        this.root.innerHTML = '';
    };

    this._patch_events = function(node, patch_input_events) {
        // TODO all events should ignore nodes when lona-widget is set

        var lona = this;

        if(patch_input_events === undefined) {
            patch_input_events = true;
        };

        // patch link onClick events
        var nodes = node.querySelectorAll('a:not(.external):not(.ignore)');

        for(let i in nodes) {
            nodes[i].onclick = function(event) {
                event.preventDefault();

                var element = event.target || event.srcElement;
                lona.run_view(element.href);

                return false;
            };
        };

        // patch form onSubmit events
        var nodes = node.querySelectorAll('form:not(.external):not(.ignore)');

        for(let i in nodes) {
            nodes[i].onsubmit = function(event) {
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

                if(patch_input_events) {
                    var data = {};

                    for(let [key, value] of form_data.entries()) {
                        if(key in multi_selects) {
                            data[key] = multi_selects[key];

                        } else {
                            data[key] = value;

                        };
                    }

                    lona.fire_input_event(
                        this, lona.INPUT_EVENT_TYPE.SUBMIT, data);

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

                        lona.run_view(href);

                    } else if(method == 'post') {
                        var post_data = {};

                        for(let [key, value] of form_data.entries()) {
                            post_data[key] = value;
                        }

                        lona.run_view(action, post_data);
                    };
                };

                return false;
            };
        };

        // input events
        if(!patch_input_events) {
            return;
        };

        // custom widgets
        var custom_widget_nodes = lona.root.querySelectorAll(
            '[lona-widget]:not([lona-widget=""])');

        if(custom_widget_nodes.length > 0) {
            for(var i in custom_widget_nodes) {
                var node = custom_widget_nodes[i];

                if(!node.getAttribute) {
                    continue;  // FIXME: Why is this possible?
                };

                var widget_name = node.getAttribute('lona-widget');

                if(lona.widget_handler[widget_name]) {
                    lona.widget_handler[widget_name](node, lona);
                };
            };
        };

        // .clickable
        var clickable_nodes = lona.root.querySelectorAll(
            '[lona-classes=clickable]');

        for(var i in clickable_nodes) {
            clickable_nodes[i].onclick = function(event) {
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

                lona.fire_input_event(
                    node, lona.INPUT_EVENT_TYPE.CLICK, event_data);

                return false;
            };
        };

        // .changeable
        var changeable_nodes = lona.root.querySelectorAll(
            '[lona-classes=changeable]');

        for(var i in changeable_nodes) {
            changeable_nodes[i].onchange = function(event) {
                event.preventDefault();

                var node = event.target || event.srcElement;
                var value = node.value;

                if(node.getAttribute('type') == 'checkbox') {
                    value = node.checked;
                };

                lona.fire_input_event(
                    node, lona.INPUT_EVENT_TYPE.CHANGE, value);

                return false;
            };
        };
    };

    this._show_html = function(data, patch_input_events) {
        // data is a complete html tree
        if(typeof(data) == 'string') {
            this._clear();
            this.root.innerHTML = data;

            this._patch_events(this.root, patch_input_events);

        // data is an update for the current html tree
        } else {
            for(let node_id in data) {
                var update_data = data[node_id];
                var node_id_string = '[lona-node-id="' + node_id + '"]';
                var node = lona.root.querySelector(node_id_string);

                if(!node) {
                    continue;
                };

                // html
                if(update_data.html) {
                    node.innerHTML = update_data.html;

                    var patch_input_events = true;  // FIXME
                    this._patch_events(node, patch_input_events);
                };

                // attributes
                if(!update_data.attributes) {
                    continue;
                };

                // style
                if(update_data.attributes.style) {
                    node.style = update_data.attributes.style;
                };
            };
        };
    };

    // public api -------------------------------------------------------------
    this.send = function(string) {
        console.debug('lona tx >>', string);

        this._ws.send(string);
    };

    this.fire_input_event = function(node, input_event_type, data) {
        if(data == undefined) {
            data = [];
        };

        if(Array.isArray(data)) {
            data = [data];
        };

        // node description
        var lona_node_id = node.getAttribute('lona-node-id');

        if(lona_node_id) {
            var node_info = [lona_node_id];

        } else {
            var node_info = [
                undefined,  // empty lona-node-id
                node.tagName,
                node.id || '',
                node.classList.value || '',
            ];
        };

        // send event message
        var window_id = 1;

        var message = [
            window_id, this.METHOD.INPUT_EVENT, this.url, input_event_type,
        ].concat(
            data,
        ).concat(
            node_info,
        );

        this.send(JSON.stringify(message));
    };

    this.widget = function(name, handler) {
        this.widget_handler[name] = handler;
    };

    this.patch_links = function(node) {
        if(typeof(node) == 'string') {
            node = document.querySelector(node);
        };

        var patch_input_events = false;

        this._patch_events(node, patch_input_events);
    };

    this.run_view = function(url, post_data) {
        // Save the requested url to only show HTML messages that are related
        // to this request.
        // This prevents glitches when switching urls fast.
        this.url = url;

        var window_id = 1;
        var message = [window_id, this.METHOD.VIEW, url];

        if(post_data) {
            message[2] = post_data;
        };

        this.send(JSON.stringify(message));
    };

    this.setup = function() {
        // setup root node
        if(typeof(this.settings.target) == 'string') {
            this.root = document.querySelector(this.settings.target);

        } else {
            this.root = this.settings.target;

        };

        this._clear();

        // setup websocket
        var protocol = 'ws://';

        if(window.location.protocol == 'https:') {
            protocol = 'wss://';
        }

        this._ws = new WebSocket(protocol + window.location.host);

        this._ws.lona = this;
        this._ws.onmessage = this._onmessage;

        // load initial page
        this._ws.onopen = function(event) {
            this.lona.run_view(document.location.href);

            // setup pushstate
            if(this.lona.settings.push_state) {
                window.onpopstate = function(event) {
                    this.lona.run_view(document.location.href);
                };
            };
        };
    };
};
