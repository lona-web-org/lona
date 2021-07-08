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
    this._rendering_hooks = [];
    this._view_timeout_hooks = [];
    this._input_event_timeout_hooks = [];
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

    // input events -----------------------------------------------------------
    this.patch_input_events = function(root_node_selector, window_id) {
        var _this = this;

        // find window
        if(window_id == undefined) {
            window_id = 1;
        };

        var _window = this._windows[window_id];

        // patch input events
        var node = document.querySelector(root_node_selector);
        var selector = 'a,form,[data-lona-events]';

        node.querySelectorAll(selector).forEach(function(node) {
            _window._input_event_handler.patch_input_events(node);
        });
    };

    // hooks ------------------------------------------------------------------
    this.add_connect_hook = function(hook) {
        this._connect_hooks.push(hook);
    };

    this.add_disconnect_hook = function(hook) {
        this._disconnect_hooks.push(hook);
    };

    this.add_rendering_hook = function(hook) {
        this._rendering_hooks.push(hook);
    };

    this.add_view_timeout_hook = function(hook) {
        this._view_timeout_hooks.push(hook);
    };

    this.add_input_event_timeout_hook = function(hook) {
        this._input_event_timeout_hooks.push(hook);
    };

    this.add_message_handler = function(handler) {
        this._message_handler.push(handler);
    };

    this._run_connect_hooks = function(event) {
        for(var i in this._connect_hooks) {
            var hook = this._connect_hooks[i];

            hook(this, event);
        };
    };

    this._run_disconnect_hooks = function(event) {
        for(var i in this._disconnect_hooks) {
            var hook = this._disconnect_hooks[i];

            hook(this, event);
        };
    };

    this._run_rendering_hooks = function(lona_window) {
        try {
            for(var i in this._rendering_hooks) {
                var hook = this._rendering_hooks[i];

                hook(this, lona_window);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    this._run_view_timeout_hooks = function(lona_window) {
        var lona_window_shim = new Lona.LonaWindowShim(this, lona_window);

        try {
            for(var i in this._view_timeout_hooks) {
                var hook = this._view_timeout_hooks[i];

                hook(this, lona_window_shim);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    this._run_input_event_timeout_hooks = function(lona_window) {
        var lona_window_shim = new Lona.LonaWindowShim(this, lona_window);

        try {
            for(var i in this._input_event_timeout_hooks) {
                var hook = this._input_event_timeout_hooks[i];

                hook(this, lona_window_shim);
            };

        } catch(error) {
            lona_window.crash(error);

        };
    };

    this._run_message_handler = function(message) {
        for(var i in this._message_handler) {
            var message_handler = this._message_handler[i];

            var return_value = message_handler(this, message);

            if(!return_value) {
                return;
            };
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

        // all lona messages have to start with a window id
        if(!Number.isInteger(json_data[0])) {
            return this.lona_context._run_message_handler(raw_message);
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
