from __future__ import annotations

from tempfile import TemporaryDirectory
import logging
import os

from lona import JsonResponse, Response

logger = logging.getLogger('lona.server.file-storage')


class FileStorageMiddleware:

    # startup / shutdown
    async def on_startup(self, data):
        self.temp_dir = TemporaryDirectory()
        self.root = self.temp_dir.name

        logger.debug('temporary directory: %r', self.root)

    async def on_shutdown(self, data):
        logger.debug('cleaning up %r', self.root)

        self.temp_dir.cleanup()

    # request handling
    def _get_token(self, url: str) -> str | None:
        if url.endswith('/'):
            url = url[:-1]

        return url.rsplit('/', 1)[1]

    async def _handle_file_upload(self, http_request, token):
        reader = await http_request.multipart()

        while True:  # FIXME: implement max_files
            field = await reader.next()

            if not field:
                break

            path = os.path.join(self.root, field.filename)
            size = 0

            with open(path, 'wb') as file_handle:
                while True:
                    chunk = await field.read_chunk()

                    if not chunk:
                        break

                    size += len(chunk)  # FIXME: implement max_size
                    file_handle.write(chunk)

            logger.info('%s bytes written to %s', size, path)

        return Response(status=200)

    def handle_http_request(self, data):
        server = data.server
        settings = server.settings
        http_request = data.http_request

        # check if request is a file storage request
        if not http_request.path.startswith(settings.FILE_STORAGE_URL_PREFIX):
            return data

        # check if token exists
        token = self._get_token(http_request.path)

        if token not in self.tokens:
            return Response(status=401)  # Unauthorized

        # upload
        if http_request.method == 'POST':
            return server.run_coroutine_sync(
                self._handle_file_upload,
                http_request,
                token,
                wait=True,
            )

        # actions
        action = http_request.query.get('action', '')
        name = http_request.query.get('name', '')

        # get

        # remove
        if action == 'remove':
            path = os.path.join(self.root, token, name)

            if os.path.exists(path):
                return Response(status=400)

            os.unlink(path)

            logger.info('%s was removed', path)

            return Response(status=200)

        # list
        if action == 'list':
            path = os.path.join(self.root, token)
            files = os.listdir(path)

            return JsonResponse(files)

        # Bad Request
        return Response(status=400)
