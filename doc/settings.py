PROJECT_NAME = 'lona'
CONTENT_ROOT = 'content'
OUTPUT_ROOT = 'output'

THEME_PATHS = [
    'theme',
]

PLUGINS = [
    'flamingo.plugins.rstPygments',
    'flamingo.plugins.Menu',
    'flamingo.plugins.Git',
    'flamingo.plugins.Thumbnails',
    'flamingo.plugins.PhotoSwipe',
    'flamingo.plugins.SphinxThemes',
]

MENU = [
    ['Documentation', [
        ['Getting Started', 'getting-started.rst'],
        ['Contributors', 'contributors.rst'],
    ]],
]

DEFAULT_GALLERY_TEMPLATE = 'photoswipe/gallery.html'
DEFAULT_IMAGE_TEMPLATE = 'photoswipe/image.html'

SPHINX_THEMES_HTML_THEME = 'sphinx_rtd_theme'
SPHINX_THEMES_LOGO = 'logo.svg'
SPHINX_THEMES_DOCSTITLE = 'Lona'
SPHINX_THEMES_SHORTTITLE = 'Lona'
SPHINX_THEMES_PROJECT = 'Lona'

SPHINX_THEMES_EXTRA_STYLESHEETS = [
    '/static/photoswipe/photoswipe.css',
    '/static/photoswipe/default-skin/default-skin.css',
    '/static/custom.css',
]

SPHINX_THEMES_EXTRA_SCRIPTS = [
    '/static/photoswipe/photoswipe.min.js',
    '/static/photoswipe/photoswipe-ui-default.min.js',
    '/static/photoswipe/photoswipe-init.js',
]
