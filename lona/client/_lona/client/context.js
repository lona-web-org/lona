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

import { LonaWindowShim } from '../client2/window-shim.js';
import { LonaWindow } from './window.js';
import { Lona } from './lona.js';


export class LonaContext {
    constructor(settings) {
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

        if(typeof(this.settings.scroll_to_top_on_view_start) == 'undefined') {
            this.settings.scroll_to_top_on_view_start = true;
        };

        this._windows = new Map();
        this._last_window_id = 0;
        this._connect_hooks = [];
        this._disconnect_hooks = [];
        this._rendering_hooks = [];
        this._view_timeout_hooks = [];
        this._input_event_timeout_hooks = [];
        this._message_handler = [];
    };

    // window -----------------------------------------------------------------
    create_window(root, url) {
        if(typeof(root) == 'string') {
            root = document.querySelector(root);
        };

        this._last_window_id += 1;

        var window_id = this._last_window_id;
        var lona_window = new LonaWindow(this, root, window_id, url);

        this._windows.set(window_id, lona_window);

        lona_window.setup(url);

        return window_id;
    };

    // input events -----------------------------------------------------------
    patch_input_events(root_node_selector, window_id) {
        // find window
        if(window_id == undefined) {
            var _window = this.get_default_window();
        } else {
            var _window = this._windows.get(window_id);
        }

        // patch input events
        var node = document.querySelector(root_node_selector);
        var selector = 'a,form,[data-lona-events]';

        node.querySelectorAll(selector).forEach(node => {
            _window._input_event_handler.patch_input_events(node);
        });
    };

    // hooks ------------------------------------------------------------------
    add_connect_hook(hook) {
        this._connect_hooks.push(hook);
    };

    add_disconnect_hook(hook) {
        this._disconnect_hooks.push(hook);
    };

    add_rendering_hook(hook) {
        this._rendering_hooks.push(hook);
    };

    add_view_timeout_hook(hook) {
        this._view_timeout_hooks.push(hook);
    };

    add_input_event_timeout_hook(hook) {
        this._input_event_timeout_hooks.push(hook);
    };

    add_message_handler(handler) {
        this._message_handler.push(handler);
    };

    _run_connect_hooks(event) {
        for(var i in this._connect_hooks) {
            var hook = this._connect_hooks[i];

            hook(this, event);
        };
    };

    _run_disconnect_hooks(event) {
        for(var i in this._disconnect_hooks) {
            var hook = this._disconnect_hooks[i];

            hook(this, event);
        };
    };

    _run_rendering_hooks(lona_window) {
        try {
            for(var i in this._rendering_hooks) {
                var hook = this._rendering_hooks[i];

                hook(this, lona_window);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    _run_view_timeout_hooks(lona_window) {
        var lona_window_shim = new LonaWindowShim(this, lona_window);

        try {
            for(var i in this._view_timeout_hooks) {
                var hook = this._view_timeout_hooks[i];

                hook(this, lona_window_shim);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    _run_input_event_timeout_hooks(lona_window) {
        var lona_window_shim = new LonaWindowShim(this, lona_window);

        try {
            for(var i in this._input_event_timeout_hooks) {
                var hook = this._input_event_timeout_hooks[i];

                hook(this, lona_window_shim);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    _run_message_handler(message) {
        for(var i in this._message_handler) {
            var message_handler = this._message_handler[i];

            var return_value = message_handler(this, message);

            if(!return_value) {
                return;
            };
        };
    };

    // websocket messages -----------------------------------------------------
    send(message) {
        if(typeof(message) != 'string') {
            message = JSON.stringify(message);
        };

        console.debug('lona tx >>', message);

        this._ws.send(message);
    };

    _handle_raw_websocket_message(event) {
        var raw_message = event.data;
        var json_data = undefined;

        console.debug('lona rx <<', raw_message);

        // all lona messages start with 'lona:'
        if(!raw_message.startsWith(Lona.protocol.PROTOCOL.MESSAGE_PREFIX)) {
            return this.lona_context._run_message_handler(raw_message);
        };

        // parse json
        try {
            raw_message = raw_message.substring(
                Lona.protocol.PROTOCOL.MESSAGE_PREFIX.length,
            );

            var json_data = JSON.parse(raw_message);

        } catch {
            return this.lona_context._run_message_handler(
                raw_message, json_data);

        };

        // all lona messages are Arrays
        if(!Array.isArray(json_data)) {
            return this.lona_context._run_message_handler(raw_message);
        };

        // all lona messages but pong messages have to start with a window id
        if(json_data[2] != Lona.protocol.METHOD.PONG &&
           !Number.isInteger(json_data[0])) {

            return this.lona_context._run_message_handler(raw_message);
        };

        var window_id = json_data[0];

        if(this.lona_context._windows.has(window_id)) {
            let lona_window = this.lona_context._windows.get(window_id);

            lona_window.handle_websocket_message(json_data);
        };
    };

    // pings ------------------------------------------------------------------
    send_ping() {
        var raw_message = [
            undefined,  // window_id
            undefined, // view_runtime_id
            Lona.protocol.METHOD.PING,  // method
            undefined,  // payload
        ]

        var message = (
            Lona.protocol.PROTOCOL.MESSAGE_PREFIX +
            JSON.stringify(raw_message)
        );

        this.send(message);
    };

    _send_pings() {
        setTimeout(
            () => {
                if(this._ws.readyState != this._ws.OPEN) {
                    return;
                };

                this.send_ping();
                this._send_pings();
            },
            Lona.settings.PING_INTERVAL * 1000,
        );
    };

    // setup ------------------------------------------------------------------
    reconnect(options) {
        var options = options || {
            create_window: true,
        };

        // state
        this._windows.clear();

        // setup websocket
        var protocol = 'ws://';

        if(window.location.protocol == 'https:') {
            protocol = 'wss://';
        }

        this._ws = new WebSocket(
            protocol + window.location.host + window.location.pathname);

        this._ws.lona_context = this;
        this._ws.options = options;
        this._ws.onmessage = this._handle_raw_websocket_message;

        // onopen
        this._ws.onopen = function(event) {
            if(this.options.create_window) {

                // load initial page
                var window_id = this.lona_context.create_window(
                    this.lona_context.settings.target,
                    document.location.href,
                );

                // setup pushstate
                if(this.lona_context.settings.update_address_bar) {
                    window.onpopstate = () => {
                        this.lona_context._windows.get(window_id).run_view(
                            document.location.href,
                        );
                    };
                };
            };

            this.lona_context._run_connect_hooks(event);
        };

        // onclose
        this._ws.onclose = function(event) {
            this.lona_context._run_disconnect_hooks(event);
        };

        // pings
        if(Lona.settings.PING_INTERVAL > 0) {
            this._send_pings();
        };
    };

    setup() {
        this.reconnect();

        // unset websocket.onclose handler when page gets unloaded to
        // prevent the browser from showing "Server disconnected" when the
        // user changes the browser URL
        window.addEventListener('beforeunload', event => {
            this._ws.onclose = event => {};
            this._ws.close();
        });
    };

    // shortcuts --------------------------------------------------------------
    get_default_window() {
        // returns the default window
        // the default window is always the window with the lowest id

        return this._windows.get(Math.min(...this._windows.keys()));
    };

    run_view(url, post_data) {
        var window = this.get_default_window();

        return window.run_view(url, post_data);
    };
};
