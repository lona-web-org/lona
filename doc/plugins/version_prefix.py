from pathlib import Path
from sys import prefix
import os

from bs4 import BeautifulSoup

from flamingo.plugins.redirects import HTML_TEMPLATE


class VersionPrefix:
    def get_prefix(self):
        return self.settings.VERSION_PREFIX

    def patch_urls(self, soup, tag_name, attribute_name):
        prefix = self.get_prefix()

        for tag in soup.find_all(tag_name):
            if not tag.has_attr(attribute_name):
                continue

            if not tag[attribute_name].startswith('/'):
                continue

            tag[attribute_name] = f"{prefix}{tag[attribute_name][1:]}"

    def settings_setup(self, context):
        self.settings = context.settings
        prefix = self.get_prefix()

        context.settings.OUTPUT_ROOT = f"output{prefix}"
        context.settings.STATIC_ROOT = f"output{prefix}static"

    def post_build(self, context):
        prefix = self.get_prefix()
        paths = []

        # find all HTML documents
        for path in Path(context.settings.OUTPUT_ROOT).rglob('*.html'):
            paths.append(str(path))

        # patch HTML documents
        for path in paths:
            soup = BeautifulSoup(open(path, 'r').read(), 'html.parser')

            self.patch_urls(soup, 'link', 'href')
            self.patch_urls(soup, 'script', 'src')
            self.patch_urls(soup, 'form', 'action')
            self.patch_urls(soup, 'a', 'href')
            self.patch_urls(soup, 'img', 'src')

            with open(path, 'w') as f:
                f.write(str(soup))

            # generate redirect
            base_path = os.path.relpath(path, context.settings.OUTPUT_ROOT)
            path = os.path.join('output', base_path)
            dirname = os.path.dirname(path)
            url = os.path.join('/', prefix, base_path)
            redirect_text = HTML_TEMPLATE.format(url)

            try:
                os.makedirs(dirname)

            except FileExistsError:
                pass

            with open(path, 'w+') as f:
                f.write(redirect_text)
