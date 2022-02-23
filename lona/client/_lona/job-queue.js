Lona.JobQueue = function(lona_window) {
    this._lona_window = lona_window;
    this._promises = [];

    this._lock = function() {
        var promise_resolve;

        var promise = new Promise(function(resolve, reject) {
            promise_resolve = resolve;
        });

        promise.resolve = promise_resolve;

        var new_array_length = this._promises.push(promise);

        if(new_array_length == 1) {
            promise.resolve();
        };

        return promise;
    };

    this._unlock = function() {
        this._promises.shift();

        if(this._promises.length > 0) {
            this._promises[0].resolve();
        };
    };

    this.add = async function(callback) {
        await this._lock();

        try {
            var promise = callback();

            if(promise instanceof Promise) {
                await promise;
            };

        } catch(error) {
            this._lona_window.crash(error);

        } finally {
            this._unlock();

        };
    };
};
