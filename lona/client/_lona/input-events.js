Lona.LonaInputEventHandler = class LonaInputEventHandler {
    constructor(lona_context, lona_window) {
        this.lona_context = lona_context;
        this.lona_window = lona_window;

        this.reset();
    };

    reset() {
        this._event_id = 1;
        this._timeouts = {};
    };

    gen_event_id() {
        var event_id = this._event_id;

        this._event_id += 1;

        return event_id;
    };

    clear_timeout(event_id) {
        clearTimeout(this._timeouts[event_id]);

        delete this._timeouts[event_id];
    };

    _get_value(node) {
        var value = node.value;

        // checkbox
        if(node.getAttribute('type') == 'checkbox') {
            value = node.checked;

        // select multiple
        } else if(node.type == 'select-multiple') {
            value = [];

            Array.from(node.selectedOptions).forEach(option => {
                value.push(option.value);
            });

        };

        return value;
    };

    _clear_input_events(node) {
        node.onclick = undefined;
        node.oninput = undefined;
        node.onchange = undefined;
        node.onfocus = undefined;
        node.onblur = undefined;
    };

    _patch_link(node) {
        var lona_window = this.lona_window;

        node.onclick = function(event) {
            event.preventDefault();

            try {
                lona_window.run_view(node.href);

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _patch_onclick(node, event_type) {
        var input_event_handler = this;
        var lona_window = this.lona_window;

        node.onclick = function(event) {
            event.preventDefault();

            try {
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
                    node,
                    Lona.protocol.INPUT_EVENT_TYPE.CLICK,
                    event_data,
                );

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _patch_onchange(node, event_type) {
        var input_event_handler = this;
        var lona_window = this.lona_window;

        var input_delay = event_type[0];

        // oninput (input delay)
        if(input_delay != undefined) {
            node.oninput = function(event) {
                event.preventDefault();

                try {
                    if(node.delay_timer !== undefined) {
                        clearTimeout(node.delay_timer);
                    }

                    node.delay_timer = setTimeout(function() {
                        var value = input_event_handler._get_value(node);

                        input_event_handler.fire_input_event(
                            node,
                            Lona.protocol.INPUT_EVENT_TYPE.CHANGE,
                            value,
                        );
                    }, input_delay);

                } catch(error) {
                    lona_window.crash(error);

                };

                return false;
            };

            return;
        };

        // onchange
        node.onchange = function(event) {
            event.preventDefault();

            try {
                var value = input_event_handler._get_value(node);

                input_event_handler.fire_input_event(
                    node,
                    Lona.protocol.INPUT_EVENT_TYPE.CHANGE,
                    value,
                );

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _patch_onsubmit(node) {
        node.onsubmit = function(event) {
            event.preventDefault();

            try {
                // find multiple selects
                var multi_selects = {};

                this.querySelectorAll('select[multiple]').forEach(
                    select_node => {
                        var name = select_node.name;

                        multi_selects[select_node.name] = [];

                        Array.from(select_node.selectedOptions).forEach(
                            option => {
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

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _patch_onfocus(node, event_type) {
        var input_event_handler = this;
        var lona_window = this.lona_window;

        node.onfocus = function(event) {
            event.preventDefault();

            try {
                input_event_handler.fire_input_event(
                    node,
                    Lona.protocol.INPUT_EVENT_TYPE.FOCUS,
                    undefined,
                );

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _patch_onblur(node, event_type) {
        var input_event_handler = this;
        var lona_window = this.lona_window;

        node.onblur = function(event) {
            event.preventDefault();

            try {
                input_event_handler.fire_input_event(
                    node,
                    Lona.protocol.INPUT_EVENT_TYPE.BLUR,
                    undefined,
                );

            } catch(error) {
                lona_window.crash(error);

            };

            return false;
        };
    };

    _parse_data_lona_events(node) {
        var event_types = {};

        if(!node.hasAttribute('data-lona-events')) {
            return event_types;
        };

        var _event_types = node.getAttribute('data-lona-events');
        _event_types = _event_types.split(';').filter(Boolean);

        _event_types.forEach((event_type, index) => {
            var raw_event_type = event_type.replace(':', ',')
            var event_type = raw_event_type.split(',').filter(Boolean);

            event_types[event_type[0]] = event_type.splice(1);
        });

        return event_types;
    };

    patch_input_events(node) {
        if(node.nodeType != Node.ELEMENT_NODE) {
            return;
        };

        // ignored nodes
        if(node.hasAttribute('data-lona-ignore')) {
            return;
        };

        var event_types = this._parse_data_lona_events(node);

        // links
        if(node.tagName == 'A' &&
           !(Lona.protocol.INPUT_EVENT_TYPE.CLICK in event_types)) {

            return this._patch_link(node);

        // forms
        } else if(node.tagName == 'FORM') {
            return this._patch_onsubmit(node);

        };

        // data-lona-input-events attribute
        Object.keys(event_types).forEach(key => {
            var event_type = event_types[key];

            // onclick
            if(key == Lona.protocol.INPUT_EVENT_TYPE.CLICK) {
                this._patch_onclick(node, event_type);

            // onchange / oninput
            } else if(key == Lona.protocol.INPUT_EVENT_TYPE.CHANGE) {
                this._patch_onchange(node, event_type);

            // onsubmit
            } else if(key == Lona.protocol.INPUT_EVENT_TYPE.SUBMIT) {
                this._patch_onsubmit(node, event_type);

            // onfocus
            } else if(key == Lona.protocol.INPUT_EVENT_TYPE.FOCUS) {
                this._patch_onfocus(node, event_type);

            // onblur
            } else if(key == Lona.protocol.INPUT_EVENT_TYPE.BLUR) {
                this._patch_onblur(node, event_type);

            };
        });
    };

    fire_input_event(node, event_type, data) {
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

        if(typeof node == 'string') {
            lona_node_id = node;

        } else if(node) {
            lona_node_id = node.getAttribute('data-lona-node-id');
            node_tag_name = node.tagName;
            node_id = node.id || '';
            node_class = node.classList.value || '';
        };

        // send event message
        var event_id = this.gen_event_id();

        var payload = [
            event_id,
            event_type,
            data,
            lona_node_id,
            node_tag_name,
            node_id,
            node_class,
        ];

        var message = [
            this.lona_window._window_id,
            this.lona_window._view_runtime_id,
            Lona.protocol.METHOD.INPUT_EVENT,
            payload,
        ]

        message = (
            Lona.protocol.PROTOCOL.MESSAGE_PREFIX +
            JSON.stringify(message)
        );

        this.lona_context.send(message);

        // setup timeout
        this._timeouts[event_id] = setTimeout(() => {
            this.lona_context._run_input_event_timeout_hooks(this);
        }, Lona.settings.INPUT_EVENT_TIMEOUT * 1000);
    };
};
