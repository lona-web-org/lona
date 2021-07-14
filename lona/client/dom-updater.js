Lona.LonaDomUpdater = function(lona_context, lona_window) {
    this.lona_context = lona_context;
    this.lona_window = lona_window;

    // helper -----------------------------------------------------------------
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

    this._get_widget_nodes = function(node_id) {
        var _this = this;

        var node_list = [];
        var widget_marker = _this.lona_window._widget_marker[node_id];
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

    // methods ----------------------------------------------------------------
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
        var _this = this;

        var target_node;
        var cursor = 0;

        // find target node
        // Widget
        if(node_id in _this.lona_window._widget_marker) {
            var marker = _this.lona_window._widget_marker[node_id];

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
            target_node = _this.lona_window._nodes[node_id];

        }

        // find start index
        while(index > 0) {
            var _node = target_node.childNodes[cursor];

            if(_node == undefined) {
                break;
            };

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

        // flatten node list
        for(var i=0; i<node_list.length; i++) {
            if(Array.isArray(node_list[i])) {
                node_list = node_list.flat();
            };
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
        var _this = this;

        var target_node;
        var cursor = 0;

        // Widget
        if(target_node_id in _this.lona_window._widget_marker) {
            var marker = _this.lona_window._widget_marker[target_node_id];
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
            target_node = _this.lona_window._nodes[node_id];

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
        var _this = this;

        // TextNode
        if(node_id in _this.lona_window._nodes) {
            _this.lona_window._nodes[node_id].remove();

            delete _this.lona_window._nodes[node_id];

        // Widget
        } else if(node_id in _this.lona_window._widget_marker) {
            var marker = _this.lona_window._widget_marker[node_id];
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

            _this.lona_window._clean_node_cache();

        // Node
        } else {
            node = _this.lona_window._nodes[node_id];

            if(node) {
                node.remove();
                _this.lona_window._clean_node_cache();
            };
        };
    };

    this._clear_node = function(node_id) {
        var _this = this;

        // Widget
        if(node_id in _this.lona_window._widget_marker) {
            var marker = _this.lona_window._widget_marker[node_id];
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

            _this.lona_window._clean_node_cache();

        // Node
        } else {
            var node = _this.lona_window._nodes[node_id];

            if(!node) {
                return;
            };

            node.innerHTML = '';
            _this.lona_window._clean_node_cache();
        };
    };

    // patches ----------------------------------------------------------------
    this._apply_patch_to_node = function(patch) {
        var protocol = Lona.protocol;
        var property_names = ['value', 'checked'];

        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var data = patch.splice(3);
        var node = this.lona_window._nodes[node_id];

        if(!node) {
            return;  // FIXME: this should throw an error
        };

        // id_list
        if(patch_type == protocol.PATCH_TYPE.ID_LIST) {

            // ADD
            if(operation == protocol.OPERATION.ADD) {
                this.lona_window._add_id(node, data[0]);

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.removeAttribute('id');

                this.lona_window._add_id(node, 'lona-' + node_id)

                for(var i in data) {
                    this.lona_window._add_id(data[0]);

                };

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                this.lona_window._remove_id(node, data[0]);

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.removeAttribute('id');

                this.lona_window._add_id(node, 'lona-' + node_id)

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
                node.classList = '';

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

                // properties
                if(property_names.indexOf(name) > -1) {
                    node[data[0]] = data[1];

                // attributes
                } else {
                    node.setAttribute(data[0], data[1]);
                }

            // RESET
            } else if(operation == protocol.OPERATION.RESET) {
                node.getAttributeNames().forEach(function(name) {
                    if(['id', 'class', 'style'].indexOf(name) > -1) {
                        return;

                    };

                    node.removeAttribute(name);

                });

                for(var name in data[0]) {
                    node.setAttribute(name, data[0][name]);
                };

            // REMOVE
            } else if(operation == protocol.OPERATION.REMOVE) {
                node.removeAttribute(data[0]);

            // CLEAR
            } else if(operation == protocol.OPERATION.CLEAR) {
                node.getAttributeNames().forEach(function(name) {
                    if(['id', 'class', 'style'].indexOf(name) > -1) {
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

    this._apply_patch_to_child_nodes = function(patch) {
        var node_id = patch[0];
        var patch_type = patch[1];
        var operation = patch[2];
        var data = patch.splice(3);

        var dom_renderer = this.lona_window._dom_renderer;

        // SET
        if(operation == Lona.protocol.OPERATION.SET) {
            var node_list = dom_renderer._render_node(data[1]);

            this._set_node(node_list, node_id, data[0]);

        // RESET
        } else if(operation == Lona.protocol.OPERATION.RESET) {
            var node_list = dom_renderer._render_nodes(data[0]);

            this._clear_node(node_id);
            this._insert_node(node_list, node_id, 0);

        // CLEAR
        } else if(operation == Lona.protocol.OPERATION.CLEAR) {
            this._clear_node(node_id);

        // INSERT
        } else if(operation == Lona.protocol.OPERATION.INSERT) {
            var node_list = dom_renderer._render_node(data[1]);

            this._insert_node(node_list, node_id, data[0])

        // REMOVE
        } else if(operation == Lona.protocol.OPERATION.REMOVE) {
            this._remove_node(data[0]);

        };
    };

    this._apply_patch = function(patch) {
        var patch_type = patch[1];

        if(patch_type == Lona.protocol.PATCH_TYPE.NODES) {
            this._apply_patch_to_child_nodes(patch);

        } else {
            this._apply_patch_to_node(patch);

        };
    };
};
