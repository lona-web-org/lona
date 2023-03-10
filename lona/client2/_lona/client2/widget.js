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


function deepCopy(object) {
    return JSON.parse(JSON.stringify(object));
}


class WidgetData {
    constructor(widget, rawWidgetData) {
        this.widget = widget;
        this._data = rawWidgetData;

        this._updateData(rawWidgetData);
    }

    _updateData() {
        this.data = deepCopy(this._data);
    }

    get(key) {
        // TODO
        throw 'not implemented';
    }

    set(key, value) {
        // TODO
        throw 'not implemented';
    }
}


export class Widget {
    constructor(lonaWindowShim, widgetClass, rootNode, rawWidgetData) {
        this.lonaWindowShim = lonaWindowShim;
        this.widgetClass = widgetClass;
        this.rootNode = rootNode;

        this.widgetData = new WidgetData(this, rawWidgetData);
        this.widgetObject = undefined;
    }

    initializeWidget() {
        this.widgetObject = new this.widgetClass(
            this.lonaWindowShim,
            this.rootNode,
            this.widgetData,
        );

        // legacy API
        // TODO: remove in 2.0
        // set data
        this.widgetObject.data = this.widgetData.data;

        // set nodes
        this.widgetObject.root_node = this.rootNode;
        this.widgetObject.nodes = [this.rootNode];

        // legacy setup hook
        if(this.widgetObject.setup !== undefined) {
            this.widgetObject.setup();
        }
    }

    destroyWidget() {
        if(this.widgetObject.destroy !== undefined) {
            this.widgetObject.destroy();
        }

        // legacy API
        // TODO: remove in 2.0
        if(this.widgetObject.deconstruct !== undefined) {
            this.widgetObject.deconstruct();
        }
    }

    runDataUpdatedHook() {
        this.widgetData._updateData();

        if(this.widgetObject.onDataUpdated !== undefined) {
            this.widgetObject.onDataUpdated(this.widgetData);

            return;
        }

        // legacy API
        // TODO: remove in 2.0
        this.widgetObject.data = this.widgetData.data;

        if(this.widgetObject.data_updated !== undefined) {
            this.widgetObject.data_updated();

            return;
        }
    }
}
