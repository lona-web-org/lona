Lona.LonaWindow = function(lona_context, root, window_id) {
    this.lona_context = lona_context;
    this._root = root;
    this._window_id = window_id;
    this._view_start_timeout = undefined;

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
    this._view_running = false;
    this._view_runtime_id = undefined;
    this._url = '';
    this._nodes = {};
    this._widget_marker = {};
    this._widget_data = {};
    this._widgets = {};
    this._widgets_to_setup = [];
    this._widgets_to_update = [];

    // html rendering helper --------------------------------------------------
    this._clear = function() {
        this._root.innerHTML = '';
        this._input_event_handler.reset();
    };

    this._clear_node_cache = function() {
        // running widget deconstructors
        for(var key in this._widgets) {
            if(this._widgets[key].deconstruct !== undefined) {
                this._widgets[key].deconstruct();
            };
        };

        // resetting node state
        this._nodes = {};
        this._widget_marker = {};
        this._widget_data = {};
        this._widgets = {}
        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    this._clean_node_cache = function() {
        var _this = this;

        // nodes
        Object.keys(_this._nodes).forEach(function(key) {
            var node = _this._nodes[key];

            if(!_this._root.contains(node)) {
                delete _this._nodes[key];
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

                // remove widget
                delete _this._widgets[key];

                // remove widget data
                delete _this._widget_data[key];

                // remove widget from _widgets_to_setup
                if(_this._widgets_to_setup.indexOf(key) > -1) {
                    _this._widgets_to_setup.splice(
                     _this._widgets_to_setup.indexOf(key), 1);
                };

                // remove widget from _widgets_to_update
                if(_this._widgets_to_update.indexOf(key) > -1) {
                    _this._widgets_to_update.splice(
                     _this._widgets_to_update.indexOf(key), 1);
                };
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

        // data_updated
        _this._widgets_to_update.forEach(function(node_id) {
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
        _this._widgets_to_update = [];
    };

    this._show_html = function(html) {
        _this = this;

        _this._job_queue.add(function() {
            var message_type = html[0];
            var data = html[1];

            // HTML
            if(message_type == Lona.protocol.DATA_TYPE.HTML) {
                var selector = 'a,form,[data-lona-events]';

                _this._root.innerHTML = data;
                _this._clean_node_cache();

                _this._root.querySelectorAll(selector).forEach(function(node) {
                    _this._input_event_handler.patch_input_events(node);
                });

            // HTML tree
            } else if(message_type == Lona.protocol.DATA_TYPE.HTML_TREE) {
                _this._clear_node_cache();

                var node_list = _this._dom_renderer._render_node(data)

                _this._clear();
                _this._dom_updater._apply_node_list(_this._root, node_list);

            // HTML update
            } else if(message_type == Lona.protocol.DATA_TYPE.HTML_UPDATE) {
                _this._widgets_to_setup = [];
                _this._widgets_to_update = [];

                data.forEach(function(patch) {
                    var patch_type = patch[1];

                    if(patch_type == Lona.protocol.PATCH_TYPE.WIDGET_DATA) {
                        _this._widget_data_updater._apply_patch(patch);

                    } else {;
                        _this._dom_updater._apply_patch(patch);

                    };

                });
            };

            _this._run_widget_hooks();
            _this.lona_context._run_rendering_hooks(_this);
        });
    };

    // public api -------------------------------------------------------------
    this.crash = function(error) {
        // encode message
        var error_string;

        if(error.stack) {
            error_string = error.stack.toString();
        } else {
            error_string = error.toString();
        };

        var message = [
            this._window_id,
            this._view_runtime_id,
            Lona.protocol.METHOD.CLIENT_ERROR,
            [error_string],
        ];

        // send message
        message = (Lona.protocol.PROTOCOL.MESSAGE_PREFIX +
                   JSON.stringify(message));

        this.lona_context.send(message);

        throw(error);
    };

    this._handle_websocket_message = function (message) {
        var window_id = message[0];
        var view_runtime_id = message[1];
        var method = message[2];
        var payload = message[3];

        // view start
        if (method == Lona.protocol.METHOD.VIEW_START) {
            clearTimeout(this._view_start_timeout);

            this._view_runtime_id = view_runtime_id;
            this._view_running = true;

            if (this.lona_context.settings.update_address_bar) {
                history.pushState({}, '', this._url);
            };

            this._clear();
            this._clear_node_cache();

            return;

        // redirect
        } else if(method == Lona.protocol.METHOD.REDIRECT) {
            // TODO: implement loop detection

            if(this.lona_context.settings.follow_redirects) {
                this.run_view(payload);

            } else {
                console.debug(
                    "lona: redirect to '" + payload + "' skipped");

            };

        // http redirect
        } else if(method == Lona.protocol.METHOD.HTTP_REDIRECT) {
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
        if(method == Lona.protocol.METHOD.DATA) {
            var title = payload[0];
            var html = payload[1];

            if(this.lona_context.settings.update_title && title) {
                document.title = title;
            };

            if(html) {
                this._show_html(html);
            };

        // input event acks
        } else if(method == Lona.protocol.METHOD.INPUT_EVENT_ACK) {
            this._input_event_handler.clear_timeout(payload);

        // view stop
        } else if(method == Lona.protocol.METHOD.VIEW_STOP) {
            this._view_running = false;

        };
    };

    this.handle_websocket_message = function(message) {
        if(this._crashed) {
            return;
        };

        try {
            return this._handle_websocket_message(message);

        } catch(error) {
            this.crash(error);

        };
    };

    this.run_view = function(url, post_data) {
        // Save the requested url to only show HTML messages that are related
        // to this request.
        // This prevents glitches when switching urls fast.

        var _this = this;

        if(this._crashed) {
            return;
        };

        // reset state
        this._view_running = false;
        this._view_runtime_id = undefined;
        this._url = url;

        // reset view start timeout
        if(this._view_start_timeout != undefined) {
            clearTimeout(this._view_start_timeout);
            this._clear();
        };

        // encode message
        var message = [
            this._window_id,
            this._view_runtime_id,
            Lona.protocol.METHOD.VIEW,
            [url, post_data],
        ];

        // update html title
        if(this.lona_context.settings.update_title &&
           this.lona_context.settings.title) {

            document.title = this.lona_context.settings.title;
        };

        // send message
        message = (Lona.protocol.PROTOCOL.MESSAGE_PREFIX +
                   JSON.stringify(message));

        this.lona_context.send(message);

        // setup view start timeout
        this._view_start_timeout = setTimeout(function() {
            _this.lona_context._run_view_timeout_hooks(_this);
        }, Lona.settings.VIEW_START_TIMEOUT * 1000);
    };

    this.setup = function(url) {
        this.run_view(url);
    };
};
