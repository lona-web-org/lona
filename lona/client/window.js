Lona.LonaWindow = function(lona_context, root, window_id) {
    this.lona_context = lona_context;
    this._root = root;
    this._window_id = window_id;

    this._job_queue = new Lona.JobQueue(this);

    this._input_event_handler = new Lona.LonaInputEventHandler(
        lona_context,
        this,
    );

    this._dom_renderer = new Lona.LonaDomRenderer(
        lona_context,
        this,
    );

    this._dom_updater = new Lona.LonaDomUpdater(
        lona_context,
        this,
    );

    this._widget_data_updater = new Lona.LonaWidgetDataUpdater(
        lona_context,
        this,
    );

    // window state -----------------------------------------------------------
    this._crashed = false;
    this._view_stopped = undefined;
    this._view_runtime_id = undefined;
    this._text_nodes = {};
    this._widget_marker = {};
    this._widget_data = {};
    this._widgets = {};
    this._widgets_to_setup = [];
    this._widgets_to_update_nodes = [];
    this._widgets_to_update_data = [];

    // error management -------------------------------------------------------
    this._print_error = function(error) {
        var error_string;

        if(error.stack) {
            error_string = error.stack.toString();

        } else {
            error_string = error.toString();

        };

        this._root.innerHTML = (
            '<h1>Lona: Uncaught Error</h1>' +
            '<pre>' + error_string + '</pre>'
        );

        throw(error);
    };

    // html rendering helper --------------------------------------------------
    this._clear = function() {
        this._root.innerHTML = '';
    };

    this._clear_node_cache = function() {
        this._text_nodes = {};
        this._widget_marker = {};
        this._widget_data = {};
        this._widgets_to_setup = [];
        this._widgets_to_update_nodes = [];
        this._widgets_to_update_data = [];
    };

    this._clean_node_cache = function() {
        var _this = this;

        // text nodes
        Object.keys(_this._text_nodes).forEach(function(key) {
            var node = _this._text_nodes[key];

            if(!_this._root.contains(node)) {
                delete _this._text_nodes[key];
            };
        });

        Object.keys(_this._widget_marker).forEach(function(key) {
            var node = _this._widget_marker[key];

            // widget_marker
            if(_this._root.contains(node)) {
                return;

            };

            delete _this._widget_marker[key];

            // widget
            if(key in _this._widgets) {

                // run deconstructor
                if(_this._widgets[key].deconstruct !== undefined) {
                    _this._widgets[key].deconstruct();
                };

                delete _this._widgets[key];
                delete _this._widget_data[key];
            };
        });
    };

    // hooks ------------------------------------------------------------------
    this._run_widget_hooks = function() {
        var _this = this;

        // setup
        _this._widgets_to_setup.forEach(function(node_id) {
            var widget = _this._widgets[node_id];
            var widget_data = _this._widget_data[node_id];

            widget.data = JSON.parse(JSON.stringify(widget_data));

            if(widget === undefined) {
                return;
            };

            widget.nodes = _this._dom_updater._get_widget_nodes(node_id);

            if(widget.setup !== undefined) {
                widget.setup();
            };
        });

        // nodes_updated
        _this._widgets_to_update_nodes.forEach(function(node_id) {
            var widget = _this._widgets[node_id];

            if(widget === undefined) {
                return;
            };

            widget.nodes = _this._dom_updater._get_widget_nodes(node_id);

            if(widget.nodes_updated !== undefined) {
                widget.nodes_updated();
            };
        });

        // data_updated
        _this._widgets_to_update_data.forEach(function(node_id) {
            var widget = _this._widgets[node_id];
            var widget_data = _this._widget_data[node_id];

            widget.data = JSON.parse(JSON.stringify(widget_data));

            if(widget === undefined) {
                return;
            };

            if(widget.data_updated !== undefined) {
                widget.data_updated();
            };
        });

        _this._widgets_to_setup = [];
        _this._widgets_to_update_nodes = [];
        _this._widgets_to_update_data = [];
    };

    this._show_html = function(html) {
        _this = this;

        _this._job_queue.add(function() {
            var message_type = html[0];
            var data = html[1];

            // HTML
            if(message_type == Lona.symbols.DATA_TYPE.HTML) {
                _this._root.innerHTML = data;
                _this._clean_node_cache();

            // HTML tree
            } else if(message_type == Lona.symbols.DATA_TYPE.HTML_TREE) {
                _this._clear_node_cache();

                var node_list = _this._dom_renderer._render_node(data)

                _this._clear();
                _this._dom_updater._apply_node_list(_this._root, node_list);

            // HTML update
            } else if(message_type == Lona.symbols.DATA_TYPE.HTML_UPDATE) {
                var patches = data[0];
                var patched_widgets = data[1];

                _this._widgets_to_setup = [];
                _this._widgets_to_update_nodes = patched_widgets;
                _this._widgets_to_update_data = [];

                patches.forEach(function(patch) {
                    var patch_type = patch[1];

                    if(patch_type == Lona.symbols.PATCH_TYPE.WIDGET_DATA) {
                        _this._widget_data_updater._apply_patch(patch);

                    } else {;
                        _this._dom_updater._apply_patch(patch);

                    };

                });
            };

            _this._input_event_handler.patch_input_events();
            _this._run_widget_hooks();

        });
    };

    // public api -------------------------------------------------------------
    this._handle_websocket_message = function(message) {
        var window_id = message[0];
        var view_runtime_id = message[1];
        var method = message[2];
        var payload = message[3];

        // view start
        if(method == Lona.symbols.METHOD.VIEW_START) {
            this._view_runtime_id = view_runtime_id;
            this._view_stopped = false;

            return;

        // redirect
        } else if(method == Lona.symbols.METHOD.REDIRECT) {
            // TODO: implement loop detection

            if(this.lona_context.settings.follow_redirects) {
                this.run_view(payload);

            } else {
                console.debug(
                    "lona: redirect to '" + payload + "' skipped");

            };

        // http redirect
        } else if(method == Lona.symbols.METHOD.HTTP_REDIRECT) {
            if(this.lona_context.settings.follow_http_redirects) {
                window.location = payload;

            } else {
                console.debug(
                    "lona: http redirect to '" + payload + "' skipped");

            };
        };

        if(this._view_runtime_id == undefined ||
           view_runtime_id != this._view_runtime_id) {

            // the runtime is not fully setup yet or the incoming message 
            // seems to be related to a previous runtime connected to this
            // window

            return;
        };

        // data
        if(method == Lona.symbols.METHOD.DATA) {
            var title = payload[0];
            var html = payload[1];

            if(this.lona_context.settings.update_title && title) {
                document.title = title;
            };

            if(html) {
                this._show_html(html);
            };

        // view stop
        } else if(method == Lona.symbols.METHOD.VIEW_STOP) {
            this._view_stopped = true;

        };
    };

    this.handle_websocket_message = function(message) {
        if(this._crashed) {
            return;
        };

        try {
            return this._handle_websocket_message(message);

        } catch(error) {
            this._crashed = true;
            this._print_error(error);

        };
    };

    this.run_view = function(url, post_data) {
        // Save the requested url to only show HTML messages that are related
        // to this request.
        // This prevents glitches when switching urls fast.

        if(this._crashed) {
            return;
        };

        this._view_runtime_id = undefined;

        var message = [
            this._window_id,
            this._view_runtime_id,
            Lona.symbols.METHOD.VIEW,
            [url, post_data],
        ];

        if(this.lona_context.settings.update_address_bar) {
            history.pushState({}, '', url);
        };

        if(this.lona_context.settings.update_title && this.lona_context.settings.title) {
            document.title = this.lona_context.settings.title;
        };

        message = Lona.symbols.PROTOCOL.MESSAGE_PREFIX + JSON.stringify(message);

        this.lona_context.send(message);
    };

    this.setup = function(url) {
        this.run_view(url);
    };
};
