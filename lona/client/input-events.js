Lona.LonaInputEventHandler = function(lona_context, lona_window) {
    this.lona_context = lona_context;
    this.lona_window = lona_window;

    this._get_input_value = function(node) {
        var value = node.value;

        // checkbox
        if(node.getAttribute('type') == 'checkbox') {
            value = node.checked;

        // select multiple
        } else if(node.type == 'select-multiple') {
            value = [];

            Array.from(node.selectedOptions).forEach(function(option) {
                value.push(option.value);
            });

        };

        return value;
    };

    this.patch_input_events = function() {
        var input_event_handler = this;
        var lona_window = this.lona_window;
        var lona_context = this.lona_context;
        var root = this.lona_window._root;

        // links
        var selector = 'a:not(.lona-clickable):not(.lona-ignore)';

        root.querySelectorAll(selector).forEach(function(node) {
            node.onclick = function(event) {
                event.preventDefault();

                try {
                    var element = event.target || event.srcElement;

                    lona_window.run_view(element.href);

                } catch(error) {
                    lona_window._crashed = true;
                    lona_window._print_error(error);

                };

                return false;
            };
        });

        // click events
        var selector = '.lona-clickable:not(.lona-ignore)';

        root.querySelectorAll(selector).forEach(function(node) {
            node.onclick = function(event) {
                event.preventDefault();

                try {
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

                    input_event_handler.fire_input_event(
                        undefined,
                        node,
                        Lona.symbols.INPUT_EVENT_TYPE.CLICK,
                        event_data,
                    );

                } catch(error) {
                    lona_window._crashed = true;
                    lona_window._print_error(error);

                };

                return false;
            };
        });

        // change events
        var selector = '.lona-changeable:not(.lona-ignore)';

        root.querySelectorAll(selector).forEach(function(node) {

            // oninput (input delay)
            if(node.type == 'text' || node.type == 'textarea') {
                var input_delay = parseInt(
                    node.getAttribute('data-lona-input-delay'));

                if(input_delay) {
                    node.oninput = function(event) {
                        event.preventDefault();

                        try {
                            var node = event.target || event.srcElement;

                            if(node.delay_timer !== undefined) {
                                clearTimeout(node.delay_timer);
                            }

                            node.delay_timer = setTimeout(function() {
                                var value = input_event_handler._get_input_value(node);

                                input_event_handler.fire_input_event(
                                    undefined,
                                    node,
                                    Lona.symbols.INPUT_EVENT_TYPE.CHANGE,
                                    value,
                                );
                            }, input_delay);

                        } catch(error) {
                            lona_window._crashed = true;
                            lona_window._print_error(error);

                        };

                        return false;
                    };

                    return;
                };
            };

            // onchange
            node.onchange = function(event) {
                event.preventDefault();

                try {
                    var node = event.target || event.srcElement;
                    var value = input_event_handler._get_input_value(node);

                    input_event_handler.fire_input_event(
                        undefined,
                        node,
                        Lona.symbols.INPUT_EVENT_TYPE.CHANGE,
                        value,
                    );

                } catch(error) {
                    lona_window._crashed = true;
                    lona_window._print_error(error);

                };

                return false;
            };
        });

        // forms
        var selector = 'form:not(.lona-ignore)';

        root.querySelectorAll(selector).forEach(function(node) {
            node.onsubmit = function(event) {
                event.preventDefault();

                try {
                    // find muliple selects
                    var multi_selects = {};

                    this.querySelectorAll('select[multiple]').forEach(
                        function(select_node) {
                            var name = select_node.name;

                            multi_selects[select_node.name] = [];

                            Array.from(select_node.selectedOptions).forEach(
                                function(option) {
                                    multi_selects[name].push(option.value);
                                }
                            );
                        }
                    );

                    // generate form data
                    var raw_form_data = new FormData(this);
                    var form_data = {};

                    for(let [key, value] of raw_form_data.entries()) {
                        if(key in multi_selects) {
                            form_data[key] = multi_selects[key];

                        } else {
                            form_data[key] = value;

                        };
                    };

                    if(!lona_window._view_stopped) {
                        input_event_handler.fire_input_event(
                            undefined,
                            node,
                            Lona.symbols.INPUT_EVENT_TYPE.SUBMIT,
                            form_data,
                        );

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
                            lona_window.run_view(action, form_data);

                        };
                    };

                } catch(error) {
                    lona_window._crashed = true;
                    lona_window._print_error(error);

                };

                return false;
            };
        });
    };

    this.fire_input_event = function(widget_id, node, event_type, data) {
        if(this.lona_window._crashed) {
            return;
        };

        if(data == undefined) {
            data = [];
        };

        // node info
        var lona_node_id = undefined;
        var node_tag_name = undefined;
        var node_id = undefined;
        var node_class = undefined;

        if(node) {
            lona_node_id = node.getAttribute('lona-node-id');

            if(lona_node_id) {
                lona_node_id = lona_node_id.substr(1);
            };

            node_tag_name = node.tagName;
            node_id = node.id || '';
            node_class = node.classList.value || '';
        };

        // send event message
        var payload = [
            event_type,
            data,
            widget_id,
            lona_node_id,
            node_tag_name,
            node_id,
            node_class,
        ];

        var message = [
            this.lona_window._window_id,
            this.lona_window._view_runtime_id,
            Lona.symbols.METHOD.INPUT_EVENT,
            payload,
        ]

        message = Lona.symbols.PROTOCOL.MESSAGE_PREFIX + JSON.stringify(message);

        this.lona_context.send(message);
    };

};
