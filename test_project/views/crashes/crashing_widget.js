function CrashingWidget(lona_window) {
    this.lona_window = lona_window;

    this.setup = function() {
        foo.bar.baz = 'foo';
    };
};

Lona.register_widget_class('crashing_widget', CrashingWidget);