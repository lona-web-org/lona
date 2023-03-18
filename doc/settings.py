from flamingo.plugins import sphinx_themes

PROJECT_NAME = 'lona'
CONTENT_ROOT = 'content'
OUTPUT_ROOT = 'output'

THEME_PATHS = [
    'theme',
]

POST_BUILD_LAYERS = [
    'overlay',
]

PLUGINS = [
    'flamingo.plugins.Menu',
    'flamingo.plugins.Git',
    'flamingo.plugins.Thumbnails',
    'flamingo.plugins.PhotoSwipe',
    'flamingo.plugins.SphinxThemes',

    'plugins/toc_tree.py::TocTree',
    'plugins/rst_setting.py::rstSetting',
    'plugins/pygments.py::rstPygments',
    'plugins/fix_search.py::FixSearch',
    'plugins/changelog.py::Changelog',
    'plugins/api_doc.py::ApiDoc',
    'plugins/prefixes.py::RemoveEmptyMenuSections',
    'plugins/prefixes.py::VersionPrefix',
    'plugins/rst_directives.py::rstDirectives',
]

MENU = [
    ['', [
        ['Basic Concept', 'basic-concept.rst'],

        ['Tutorial', [
            ['1. Getting Started', 'tutorial/01-getting-started/index.rst'],
            ['2. HTML', 'tutorial/02-html/index.rst'],
            ['3. Events', 'tutorial/03-events/index.rst'],
            ['4. User Input', 'tutorial/04-user-input/index.rst'],
            ['5. Routing', 'tutorial/05-routing/index.rst'],
            ['6. Responses', 'tutorial/06-responses/index.rst'],
            ['7. Daemon Views', 'tutorial/07-daemon-views/index.rst'],
            ['8. State', 'tutorial/08-state/index.rst'],
            ['9. Middlewares', 'tutorial/09-middlewares/index.rst'],
            ['10. Static Files', 'tutorial/10-static-files/index.rst'],
            ['11. Widgets', 'tutorial/11-widgets/index.rst'],
            ['12. Frontends', 'tutorial/12-frontends/index.rst'],
        ]],

        ['Demos', [
            ['Counter', 'demos/counter/index.rst'],

            ['Bootstrap 5 Confirmation Popup',
            'demos/bootstrap-5-confirmation-popup/index.rst'],

            ['Function Plotter', 'demos/function-plotter/index.rst'],
            ['Daemonized View', 'demos/daemonized-view/index.rst'],
            ['Multi User Chat', 'demos/multi-user-chat/index.rst'],
            ['Game Of Life', 'demos/game-of-life/index.rst'],
        ]],

        ['API Reference', [
            ['Lona Scripts', 'api-reference/lona-scripts.rst'],
            ['Views', 'api-reference/views.rst'],
            ['Server', 'api-reference/server.rst'],
            ['HTML', 'api-reference/html.rst'],
            ['Frontends', 'api-reference/frontends.rst'],
            ['Error Views', 'api-reference/error-views.rst'],
            ['Middlewares', 'api-reference/middlewares.rst'],
            ['Settings', 'api-reference/settings.rst'],
            ['Sessions', 'api-reference/sessions.rst'],
            ['Testing', 'api-reference/testing.rst'],
            ['Lona Shell', 'api-reference/lona-shell.rst'],
            ['Debugging', 'api-reference/debugging.rst'],
            ['Deployment', 'api-reference/deployment.rst'],
        ]],

        [['Contrib'], [
            ['Pico.css', 'contrib/lona-picocss/index.rst'],
            ['Django', 'contrib/django/index.rst'],
            ['Bootstrap 5', 'contrib/bootstrap-5/index.rst'],
            ['Chart.js', 'contrib/chartjs/index.rst'],
        ]],

        ['Cookbook', [
            ['Using Traditional HTML', 'cookbook/using-traditional-html.rst'],
            ['Writing A Lona Form', 'cookbook/writing-a-lona-form.rst'],

            ['Writing A Traditional Form',
            'cookbook/writing-a-traditional-form.rst'],

            ['Auto-Reconnect', 'cookbook/auto-reconnect.rst'],
            ['URL Reverse Resolving', 'cookbook/url-reverse-resolving.rst'],
            ['Using Server State', 'cookbook/using-server-state.rst'],

            ['Integrating A Frontend Library',
            'cookbook/integrating-a-frontend-library.rst'],

            ['Integrating Django', 'cookbook/integrating-django.rst'],
            ['Limit Concurrent Views', 'cookbook/limit-concurrent-views.rst'],

            ['Adding A Custom Command To Lona Shell',
            'cookbook/adding-a-custom-command-to-lona-shell.rst'],
        ]],

        ['FAQ', 'faq.rst'],
        ['News / Getting Help', 'news-getting-help.rst'],
        ['How To Contribute', 'how-to-contribute.rst'],
        ['Contributors', 'contributors.rst'],
        ['Changelog', 'changelog.rst'],
        ['License', 'license.rst'],
        ['Stickers', 'stickers.rst'],
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

sphinx_themes.defaults.SPHINX_THEMES_METATAGS = """
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5">
    <meta name="msapplication-TileColor" content="#da532c">
    <meta name="theme-color" content="#ffffff">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
"""

VERSION_PREFIX = '/1.x/'
