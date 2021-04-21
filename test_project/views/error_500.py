from lona.default_views import Error500View as _Error500View


class Error500View(_Error500View):
    def handle_request(self, request, **extra_contenxt):
        if request.url.path == '/crashes/handle-500/':
            raise ValueError('Success! This should crash!')

        return self.render_default_template(request, **extra_contenxt)
