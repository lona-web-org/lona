PROJECT_NAME = 'lona'
CONTENT_ROOT = 'content'
OUTPUT_ROOT = 'output'

THEME_PATHS = [
    'theme',
]

PLUGINS = [
    'flamingo.plugins.rstPygments',
    'flamingo.plugins.Menu',
    'flamingo.plugins.ReadTheDocs',
    'flamingo.plugins.Git',
]

MENU = [
    ['Documentation', [
        ['Protocol', 'protocol.rst'],
        ['Routing', 'routing.rst'],
        ['HTML Nodes', 'nodes.rst'],
        ['Views', 'views.rst'],
    ]],
]
