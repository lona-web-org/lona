import json

from bs4 import BeautifulSoup


class FixSearch:
    def pre_build(self, context):
        _original_find_static_dirs = context.templating_engine.find_static_dirs

        def find_static_dirs():
            return _original_find_static_dirs() + ['theme/static']

        context.templating_engine.find_static_dirs = find_static_dirs

    def templating_engine_setup(self, context, templating_engine):
        def safe_dump(html):
            if not html:
                return '""'

            soup = BeautifulSoup(str(html), 'html.parser')

            while True:
                script = soup.find('script')

                if not script:
                    break

                script.decompose()

            return json.dumps(str(soup.getText()))

        def sort_by_search_index_weight(contents):
            def key(content):
                return content.get('search_index_weight', 0)

            return sorted(contents, key=key, reverse=True)

        context.settings.EXTRA_CONTEXT['safe_dump'] = safe_dump

        context.settings.EXTRA_CONTEXT['sort_by_search_index_weight'] = \
            sort_by_search_index_weight
