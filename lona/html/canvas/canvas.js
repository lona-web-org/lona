function LonaCanvasWidget(lona_window) {
    this.lona_window = lona_window;

    this._run_operations = function() {
        for(var index in this.data['operations']) {
            var operation = this.data['operations'][index];

            // set
            if(operation[0] == 'set') {
                eval('this.ctx.' + operation[1] + ' = operation[2];');

            // call
            } else if(operation[0] == 'call') {
                eval('this.ctx.' + operation[1] + '(...operation[2])');

            };
        };
    };

    this.setup = function() {
        var lona_window = this.lona_window;

        this.canvas = this.nodes[0];
        this.ctx = this.canvas.getContext(this.data['context']);

        this._run_operations();
    };

    this.data_updated = function() {
        this._run_operations();
    };
};

Lona.register_widget_class('LonaCanvasWidget', LonaCanvasWidget);
