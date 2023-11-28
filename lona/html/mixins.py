from lona.static_files import StyleSheet, SORT_ORDER, Script


class FrontendComponent:
    STATIC_FILES = [
        StyleSheet(
            name='_lona/widgets.css',
            path='widgets.css',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
        Script(
            name='_lona/widgets.js',
            path='widgets.js',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
    ]
