Lona.LonaDomRenderer = function(lona_context, lona_window) {
    this.lona_context = lona_context;
    this.lona_window = lona_window;

    // html rendering ---------------------------------------------------------
    this._render_node = function(node_spec) {
        var _this = this;
        var property_names = ['value', 'checked'];

        var node_list = [];
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

            var node = document.createElement(node_tag_name);

            // lona node id
            node.setAttribute('data-lona-node-id', node_id);

            // id list
            if(node_id_list.length > 0) {
                _this.lona_window._dom_updater._add_id(node, node_id_list);
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

                    // properties
                    if(property_names.indexOf(key) > -1) {
                        node[key] = node_attributes[key];

                    // attributes
                    } else {
                        node.setAttribute(key, node_attributes[key]);

                    };
                });
            };

            // nodes
            node_child_nodes.forEach(function(sub_node_argspec) {
                var sub_node_list = _this._render_node(
                    sub_node_argspec);

                _this.lona_window._dom_updater._apply_node_list(
                    node,
                    sub_node_list,
                );
            });

            _this.lona_window._nodes[node_id] = node;
            node_list.push(node);

        // TextNode
        } else if(node_type == Lona.protocol.NODE_TYPE.TEXT_NODE) {
            var node_id = node_spec[1];
            var node_content = node_spec[2];

            var node = document.createTextNode(node_content);

            _this.lona_window._nodes[node_id] = node;
            node_list.push(node);

        // Widget
        } else if(node_type == Lona.protocol.NODE_TYPE.WIDGET) {
            var node_id = node_spec[1];
            var node_widget_class_name = node_spec[2];
            var node_child_nodes = node_spec[3];
            var widget_data = node_spec[4];

            // setup marker
            var start_marker = document.createComment(
                'lona-widget:' + node_id);

            var end_marker = document.createComment(
                'end-lona-widget:' + node_id);

            _this.lona_window._widget_marker[node_id] = start_marker;

            node_list.push(start_marker);

            // nodes
            node_child_nodes.forEach(function(sub_node_argspec) {
                var sub_node_list = _this._render_node(
                    sub_node_argspec);

                node_list.push(sub_node_list);
            });

            // append end marker
            node_list.push(end_marker);

            // setup widget
            if(node_widget_class_name in Lona.widget_classes) {
                widget_class = Lona.widget_classes[node_widget_class_name];

                var window_shim = new Lona.LonaWindowShim(
                    lona_context,
                    _this.lona_window,
                    node_id,
                );

                var widget = new widget_class(window_shim);

                _this.lona_window._widgets[node_id] = widget;
                _this.lona_window._widget_data[node_id] = widget_data;
                _this.lona_window._widgets_to_setup.splice(0, 0, node_id);
            };
        };

        // patch input events
        node_list.forEach(function(node) {
            _this.lona_window._input_event_handler.patch_input_events(node);
        });

        return node_list;
    };

    this._render_nodes = function(node_specs) {
        // TODO: get rid of this method and move functionality
        // into _render_node()

        var _this = this;
        var node_list = [];

        for(var index in node_specs) {
            node_list = node_list.concat(this._render_node(node_specs[index]));
        };

        // patch input events
        node_list.forEach(function(node) {
            _this.lona_window._input_event_handler.patch_input_events(node);
        });

        return node_list;
    };
};
