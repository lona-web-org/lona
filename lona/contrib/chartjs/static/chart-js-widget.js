function ChartJsWidget(lona_window) {
    this.lona_window = lona_window;

    this.setup = function() {
        this.ctx = this.nodes[0].getContext('2d');
        this.chart = new Chart(this.ctx, this.data);
    };

    this.data_updated = function() {
        this.chart.data = this.data.data;
        this.chart.update();
    };
};

Lona.register_widget_class('chart_js', ChartJsWidget);
