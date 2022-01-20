function AutoCompleteWidget(lona_window) {
    this.lona_window = lona_window;

    this.promise_resolve = undefined;
    this.promise = undefined;

    this.data_updated = function() {
        this.promise_resolve();
    };

    this.setup = function() {
        var _this = this;
        var input_node = this.nodes[0];

        $(input_node).autocomplete({
            source: async function(request, response) {
                _this.promise = new Promise(function(resolve, reject) {
                    _this.promise_resolve = resolve;
                });

                _this.lona_window.fire_input_event(
                    undefined,
                    'autocomplete-request',
                    {
                        term: request.term,
                    },
                );

                await _this.promise;

                response(_this.data['results']);
            },
        });
    };
};

Lona.register_widget_class('AutoCompleteWidget', AutoCompleteWidget);
