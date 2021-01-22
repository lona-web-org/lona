from lona.static_files import StyleSheet, Script, SORT_ORDER
from lona.html import Widget, Canvas

STATIC_FILES = [
    # styesheets
    StyleSheet(
        name='chart_css_min',
        path='static/Chart.min.css',
        url='Chart.min.css',
        sort_order=SORT_ORDER.FRAMEWORK,
    ),
    StyleSheet(
        name='chart_css_min',
        path='static/Chart.css',
        url='Chart.min.css',
        sort_order=SORT_ORDER.FRAMEWORK,
        link=False,
    ),

    # scripts
    Script(
        name='chart_bundle_js_min',
        path='static/Chart.bundle.min.js',
        url='Chart.bundle.min.js',
        sort_order=SORT_ORDER.FRAMEWORK,
    ),
    Script(
        name='chart_bundle_js',
        path='static/Chart.bundle.js',
        url='Chart.bundle.js',
        sort_order=SORT_ORDER.FRAMEWORK,
        link=False,
    ),
    Script(
        name='chart_js_widget_js',
        path='static/chart-js-widget.js',
        url='chart-js-widget.js',
        sort_order=SORT_ORDER.LIBRARY,
    ),
]


class Chart(Widget):
    STATIC_FILES = STATIC_FILES
    FRONTEND_WIDGET_CLASS = 'chart_js'

    def __init__(self, **kwargs):
        self.nodes = [
            Canvas(),
        ]

        self.data = {
            **kwargs,
        }
