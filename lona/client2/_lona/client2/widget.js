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

'use strict';

import { LonaWindowShim } from './window-shim.js';


function deepCopy(object) {
    return JSON.parse(JSON.stringify(object));
}


class WidgetData {
    constructor(widget) {
        this._widget = widget;

        this.data = {};

        this._update_data();
    }

    _update_data() {
        this.data = deepCopy(this._widget.raw_widget_data);
    }
}


export class Widget {
    constructor(
            lona_context,
            lona_window,
            root_node,
            widget_id,
            widget_class,
            raw_widget_data,
    ) {

        this.lona_context = lona_context;
        this.lona_window = lona_window;
        this.root_node = root_node;
        this.widget_id = widget_id;
        this.widget_class = widget_class;
        this.raw_widget_data = raw_widget_data;

        this.window_shim = new LonaWindowShim(
            this.lona_context,
            this.lona_window,
            this.widget_id,
        );

        this.widget_data = new WidgetData(this);

        this.widget_object = undefined;

        // legacy API ---------------------------------------------------------
        // TODO: remove in 2.0
        this.nodes = [];

        if(Array.isArray(this.root_node)) {
            this.nodes = this.root_node;
            this.root_node = this.root_node[0];

        } else {
            this.nodes = [this.root_node];
        }
    }

    initialize_widget() {
        this.widget_object = new this.widget_class(
            this.window_shim,
            this.root_node,
            this.widget_data,
        );

        // legacy API
        // TODO: remove in 2.0
        // set data
        this.widget_object.data = this.widget_data.data;

        // set nodes
        this.widget_object.root_node = this.root_node;
        this.widget_object.nodes = this.nodes;

        // legacy setup hook
        if(this.widget_object.setup !== undefined) {
            this.widget_object.setup();
        }
    }

    destroy_widget() {
        if(this.widget_object === undefined) {
            return;
        }

        if(this.widget_object.destroy !== undefined) {
            this.widget_object.destroy();
        }

        // legacy API
        // TODO: remove in 2.0
        if(this.widget_object.deconstruct !== undefined) {
            this.widget_object.deconstruct();
        }
    }

    run_data_updated_hook() {
        if(this.widget_object === undefined) {
            return;
        }

        this.widget_data._update_data();

        if(this.widget_object.onDataUpdated !== undefined) {
            this.widget_object.onDataUpdated(this.widget_data);
        }

        // legacy API
        // TODO: remove in 2.0
        this.widget_object.data = this.widget_data.data;

        if(this.widget_object.data_updated !== undefined) {
            this.widget_object.data_updated();

            return;
        }
    }
}
