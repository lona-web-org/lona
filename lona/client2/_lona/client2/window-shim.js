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

export class LonaWindowShim {
    constructor(lona_context, lona_window, widget_id) {
        this.lona_context = lona_context;

        this._lona_window = lona_window;
        this._widget_id = widget_id;

        this.root_node = this._lona_window._root;
    };

    fire_input_event(node, event_type, data, target_node) {
        return this._lona_window._input_event_handler.fire_input_event(
            node || this._widget_id,
            event_type,
            data,
            target_node,
        );
    };

    set_html(html) {
        if(this._lona_window._view_running) {
            throw('RuntimeError: cannot set HTML while a view is running');
        };

        this._lona_window._root.innerHTML = html;
    };
};
