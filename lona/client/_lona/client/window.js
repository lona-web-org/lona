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

import { LonaWidgetDataUpdater } from './widget-data-updater.js'
import { LonaInputEventHandler } from './input-events.js';
import { LonaDomRenderer } from './dom-renderer.js';
import { LonaDomUpdater } from './dom-updater.js';
import { Lona } from './lona.js'


export class LonaWindow {
    constructor(lona_context, root, window_id) {
        this.lona_context = lona_context;
        this._root = root;
        this._window_id = window_id;
        this._view_start_timeout = undefined;

        this._input_event_handler = new LonaInputEventHandler(
            lona_context,
            this,
        );

        this._dom_renderer = new LonaDomRenderer(
            lona_context,
            this,
        );

        this._dom_updater = new LonaDomUpdater(
            lona_context,
            this,
        );

        this._widget_data_updater = new LonaWidgetDataUpdater(
            lona_context,
            this,
        );

        this._crashed = false;
        this._view_running = false;
        this._view_runtime_id = undefined;
        this._url = new URL(window.location);
        this._nodes = {};
        this._widget_marker = {};
        this._widget_data = {};
        this._widgets = {};
        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    // urls -------------------------------------------------------------------
    _set_url(raw_url) {
        this._url = new URL(raw_url, this._url);
    };

    get_url() {
        return this._url;
    };

    // html rendering helper --------------------------------------------------
    _clear() {
        this._root.innerHTML = '';
        this._input_event_handler.reset();
    };

    _clear_node_cache() {
        // running widget deconstructors
        for(var key in this._widgets) {
            this._widgets[key].destroy_widget();
        };

        // resetting node state
        this._nodes = {};
        this._widget_marker = {};
        this._widget_data = {};
        this._widgets = {}
        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    _remove_widget_if_present(node_id) {
        if(!(node_id in this._widgets)) {
            return;
        }

        // run deconstructor
        this._widgets[node_id].destroy_widget();

        // remove widget
        delete this._widgets[node_id];

        // remove widget data
        delete this._widget_data[node_id];

        // remove widget from _widgets_to_setup
        if(this._widgets_to_setup.indexOf(node_id) > -1) {
            this._widgets_to_setup.splice(
                this._widgets_to_setup.indexOf(node_id), 1);
        };

        // remove widget from _widgets_to_update
        if(this._widgets_to_update.indexOf(node_id) > -1) {
            this._widgets_to_update.splice(
                this._widgets_to_update.indexOf(node_id), 1);
        };
    }

    _clean_node_cache() {
        // nodes
        Object.keys(this._nodes).forEach(key => {
            var node = this._nodes[key];

            if(!this._root.contains(node)) {
                delete this._nodes[key];
            };
        });

        Object.keys(this._widget_marker).forEach(key => {
            var node = this._widget_marker[key];

            // widget_marker
            if(this._root.contains(node)) {
                return;

            };

            delete this._widget_marker[key];

            // frontend widget
            this._remove_widget_if_present(key);
        });
    };

    // hooks ------------------------------------------------------------------
    _run_widget_hooks() {
        // setup
        this._widgets_to_setup.forEach(node_id => {
            if(this._widgets[node_id] === undefined) {
                return;
            }

            const widget = this._widgets[node_id];

            widget.initialize_widget();
        });

        // data_updated
        this._widgets_to_update.forEach(node_id => {
            if(this._widgets[node_id] === undefined) {
                return;
            }

            const widget = this._widgets[node_id];

            widget.run_data_updated_hook();
        });

        this._widgets_to_setup = [];
        this._widgets_to_update = [];
    };

    _show_html(html) {
        var message_type = html[0];
        var data = html[1];

        // HTML
        if (message_type == Lona.protocol.DATA_TYPE.HTML) {
            var selector = 'a,form,[data-lona-events]';

            this._root.innerHTML = data;
            this._clean_node_cache();

            this._root.querySelectorAll(selector).forEach(node => {
                this._input_event_handler.patch_input_events(node);
            });

        // HTML tree
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_TREE) {
            this._clear_node_cache();

            var node_list = this._dom_renderer._render_node(data)

            this._clear();
            this._dom_updater._apply_node_list(this._root, node_list);

        // HTML update
        } else if(message_type == Lona.protocol.DATA_TYPE.HTML_UPDATE) {
            this._widgets_to_setup = [];
            this._widgets_to_update = [];

            data.forEach(patch => {
                var patch_type = patch[1];

                if(patch_type == Lona.protocol.PATCH_TYPE.WIDGET_DATA) {
                    this._widget_data_updater._apply_patch(patch);

                } else {
                    this._dom_updater._apply_patch(patch);

                };

                this._clean_node_cache();
            });
        };

        this._run_widget_hooks();
        this.lona_context._run_rendering_hooks(this);
    };

    // public api -------------------------------------------------------------
    crash(error) {
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

    _handle_websocket_message(message) {
        var window_id = message[0];
        var view_runtime_id = message[1];
        var method = message[2];
        var payload = message[3];

        // pong
        if(method == Lona.protocol.METHOD.PONG) {
            return;

        // view start
        } else if(method == Lona.protocol.METHOD.VIEW_START) {
            clearTimeout(this._view_start_timeout);

            this._view_runtime_id = view_runtime_id;
            this._view_running = true;

            if(this.lona_context.settings.update_address_bar) {
                history.pushState({}, '', this.get_url().href);
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
                this._set_url(payload);

                window.location = this.get_url().href;

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

    handle_websocket_message(message) {
        if(this._crashed) {
            return;
        };

        try {
            return this._handle_websocket_message(message);

        } catch(error) {
            this.crash(error);

        };
    };

    run_view(url, post_data) {
        // Save the requested url to only show HTML messages that are related
        // to this request.
        // This prevents glitches when switching urls fast.

        if(this._crashed) {
            return;
        };

        // reset state
        this._view_running = false;
        this._view_runtime_id = undefined;
        this._set_url(url);

        // reset view start timeout
        if(this._view_start_timeout != undefined) {
            clearTimeout(this._view_start_timeout);
            this._clear();
        };

        // scroll to top
        // If the a new view gets started with the page scrolled down, and
        // the page has a fixed height set in css, for example the min-height
        // of the body is set to 100%, the new view starts scrolled to the
        // bottom, which is counterintuitive to end users.
        if(this.lona_context.settings.scroll_to_top_on_view_start) {
            window.scrollTo(0, 0);
        };

        // encode message
        var message = [
            this._window_id,
            this._view_runtime_id,
            Lona.protocol.METHOD.VIEW,
            [this.get_url().href, post_data],
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
        this._view_start_timeout = setTimeout(() => {
            this.lona_context._run_view_timeout_hooks(this);
        }, Lona.settings.VIEW_START_TIMEOUT * 1000);
    };

    setup(url) {
        this.run_view(url);
    };
};
