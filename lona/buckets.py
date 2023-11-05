from __future__ import annotations

from tempfile import TemporaryDirectory
from threading import Lock
import logging
import os

from lona import HttpRedirectResponse, TemplateResponse, FileResponse, Response
from lona.unique_ids import generate_unique_id2

logger = logging.getLogger('lona.buckets')


class Bucket:
    _lock: Lock = Lock()

    _buckets: dict = {
        # request.id: {
        #     bucket.id: bucket
        # }
    }

    @classmethod
    def _open_bucket(cls, request, bucket):
        with cls._lock:
            if request.id not in cls._buckets:
                cls._buckets[request.id] = {}

            cls._buckets[request.id][bucket.id] = bucket

        logger.info(
            'bucket opened (request=%s, bucket=%s)',
            request.id,
            bucket.id,
        )

    @classmethod
    def _get_bucket(cls, request_id, bucket_id):
        with cls._lock:
            if (request_id in cls._buckets and
                    bucket_id in cls._buckets[request_id]):

                return cls._buckets[request_id][bucket_id]

    @classmethod
    def _close_buckets(cls, request):
        buckets = {}

        with cls._lock:
            if request.id in cls._buckets:
                buckets.update(cls._buckets.pop(request.id))

        for bucket in buckets.values():
            bucket._temp_dir.cleanup()

            logger.info(
                'bucket closed (request=%s, bucket=%s)',
                request.id,
                bucket.id,
            )

    def __init__(
            self,
            request,
            max_files=None,
            max_size=None,
            index=True,
            on_add=None,
            on_delete=None,
    ):

        """
        :request:    `lona.Request` object

        :max_files:  Maximum of files that can be added (uploaded) to the
                     bucket as integer. If max_files is `None` any amount of
                     files is allowed.

        :max_size:   Maximum of bytes that can be added (uploaded) to the
                     bucket as integer. If max_size is `None` any amount of
                     bytes is allowed.

        :index:      HTTP/HTML index is enabled.

        :on_add:     Optional callback which is called with the list of added
                     file names, when one or more files are added in a
                     POST request.

        :on_delete:  Optional callback which is called with the list of deleted
                     file names, when one or more files are deleted in a
                     POST request.
        """

        self.request = request
        self.max_files = max_files
        self.max_size = max_size
        self.index = index
        self.on_add = on_add
        self.on_delete = on_delete

        self._write_lock = Lock()
        self._id = generate_unique_id2()
        self._temp_dir = TemporaryDirectory()
        self._open_bucket(request=request, bucket=self)

    def __repr__(self):
        return f'<Bucket(path={self.get_path()!r}, {self.index=}, {self.max_files=}, {self.max_size=})>'

    @property
    def id(self):
        return self._id

    def get_path(self, file_name=''):
        """
        Returns the absolute path to the given file name, as a string. If no
        file name is given, the absolute path to the buckets directory is
        returned.

        :file_name: optional string file name
        """

        path = self._temp_dir.name

        if file_name:
            if file_name.startswith('/'):
                file_name = file_name[1:]

            path = os.path.join(path, file_name)

        return path

    def get_file_names(self):
        """
        Returns a list of all file names in the bucket as strings.
        """

        return os.listdir(self.get_path())

    def get_size(self):
        """
        Returns the sum of the sizes of all files in bytes, contained in the
        bucket, as integer.
        """

        size = 0

        for entry in os.scandir(self.get_path()):
            size += entry.stat().st_size

        return size

    def get_url(self, file_name=''):
        """
        Returns the URL to the given file name, as a string. If no file
        name is given, the URL to the buckets index is returned.

        :file_name: optional string file name
        """

        prefix = self.request.server.settings.BUCKETS_URL_PREFIX

        if prefix.startswith('/'):
            prefix = prefix[1:]

        if prefix.endswith('/'):
            prefix = prefix[:-1]

        url = f'/{prefix}/{self.request.id}/{self.id}'

        if file_name:
            url = f'{url}/{file_name}'

        return url

    def get_add_url(self):
        """
        Returns the add (upload) URL of the bucket as a string.
        """

        return self.get_url(file_name='add')

    def get_delete_url(self):
        """
        Returns the delete URL of the bucket as a string.
        """

        return self.get_url(file_name='delete')


class BucketsMiddleware:
    async def _handle_file_upload(self, http_request, request_id, bucket):
        file_names = []
        files_written = len(bucket.get_file_names())
        bytes_written = bucket.get_size()

        async for field in (await http_request.multipart()):
            if not field.filename:
                continue

            rel_path = field.filename
            abs_path = os.path.join(bucket.get_path(file_name=rel_path))
            file_size = 0

            # check if upload exceeds bucket.max_files
            if (bucket.max_files is not None and
                    files_written + 1 > bucket.max_files):

                logger.info(
                    '%s exceeds the buckets max files (request=%s, bucket=%s)',
                    rel_path,
                    request_id,
                    bucket.id,
                )

                return file_names, 'too many files uploaded'

            # write file to file system
            file_names.append(rel_path)
            files_written += 1

            with open(abs_path, 'wb') as file_handle:
                while True:
                    chunk = await field.read_chunk()
                    chunk_size = len(chunk)

                    if chunk_size == 0:
                        break

                    # check if upload exceeds bucket.max_size
                    if (bucket.max_size is not None and
                            bytes_written + chunk_size > bucket.max_size):

                        logger.info(
                            '%s exceeds the buckets max size (request=%s, bucket=%s)',
                            rel_path,
                            request_id,
                            bucket.id,
                        )

                        return file_names, 'too much data uploadad'

                    file_handle.write(chunk)
                    file_size += chunk_size
                    bytes_written += chunk_size

            logger.info(
                '%s bytes written to %s (request=%s, bucket=%s)',
                file_size,
                abs_path,
                request_id,
                bucket.id,
            )

        return file_names, ''

    def handle_http_request(self, data):
        server = data.server
        settings = server.settings
        http_request = data.http_request
        redirect_url = http_request.query.get('redirect', '')

        def success():
            if redirect_url:
                return HttpRedirectResponse(redirect_url)

            return Response(status=200)

        # check if request is a bucket request
        if not http_request.path.startswith(settings.BUCKETS_URL_PREFIX):
            return data

        # parse request
        # valid requests:
        #     POST /<BUCKETS_URL_PREFIX>/<request_id>/<bucket_id>/<add>
        #     POST /<BUCKETS_URL_PREFIX>/<request_id>/<bucket_id>/<delete>
        #     GET  /<BUCKETS_URL_PREFIX>/<request_id>/<bucket_id>/<file_name>
        #     GET  /<BUCKETS_URL_PREFIX>/<request_id>/<bucket_id>(/)
        path_parts = [part for part in http_request.path.split('/') if part]

        if len(path_parts) < 3 or len(path_parts) > 4:
            return data

        if len(path_parts) < 4:
            path_parts.append('')  # empty file name

        _, request_id, bucket_id, file_name_or_action = path_parts
        bucket = Bucket._get_bucket(request_id=request_id, bucket_id=bucket_id)

        if file_name_or_action in ('add', 'delete'):
            action = file_name_or_action
            file_name = ''

        else:
            action = ''
            file_name = file_name_or_action

        # search bucket
        if not bucket:
            return Response(status=404)

        # handle request
        if http_request.method == 'POST':

            # file upload
            if action == 'add':

                # check content type
                if not http_request.content_type.startswith('multipart/'):
                    return Response(status=400)

                # we have to lock the bucket for writing so bucket.max_files
                # and bucket.max_size are not overrun by multiple
                # concurrent requests
                with bucket._write_lock:
                    uploaded_files, error_message = server.run_coroutine_sync(
                        self._handle_file_upload(
                            http_request=http_request,
                            request_id=request_id,
                            bucket=bucket,
                        ),
                        wait=True,
                    )

                if error_message:
                    for rel_path in uploaded_files:
                        abs_path = os.path.join(
                            bucket.get_path(file_name=rel_path),
                        )

                        os.unlink(abs_path)

                        logger.info(
                            '%s was deleted (request=%s, bucket=%s)',
                            abs_path,
                            request_id,
                            bucket_id,
                        )

                    return Response(status=400, text=error_message)

                # bucket.on_add hook
                if uploaded_files and bucket.on_add:
                    logger.debug(
                        'running %s (request=%s, bucket=%s)',
                        bucket.on_add,
                        request_id,
                        bucket_id,
                    )

                    try:
                        bucket.on_add(uploaded_files)

                    except Exception:
                        logger.exception(
                            'Exception raised while running %s (request=%s, bucket=%s)',
                            bucket.on_add,
                            request_id,
                            bucket_id,
                        )

                return success()

            # file deletion
            elif action == 'delete':
                post_data = server.run_coroutine_sync(
                    http_request.post(),
                    wait=True,
                )

                if 'name' not in post_data:
                    return Response(status=400)

                rel_path = post_data['name']
                abs_path = os.path.join(bucket.get_path(file_name=rel_path))

                if not os.path.exists(abs_path):
                    return Response(status=404)

                logger.info(
                    '%s deleting (request=%s, bucket=%s)',
                    abs_path,
                    request_id,
                    bucket_id,
                )

                os.unlink(abs_path)

                # bucket.on_delete hook
                if bucket.on_delete:
                    logger.debug(
                        'running %s (request=%s, bucket=%s)',
                        bucket.on_delete,
                        request_id,
                        bucket_id,
                    )

                    try:
                        bucket.on_delete([rel_path])

                    except Exception:
                        logger.exception(
                            'Exception raised while running %s (request=%s, bucket=%s)',
                            bucket.on_add,
                            request_id,
                            bucket_id,
                        )

                return success()

            # invalid action
            else:
                return Response(status=400)

        # index
        if not bucket.index:
            return Response(status=401)

        if file_name:
            abs_path = os.path.join(bucket.get_path(file_name=file_name))

            if not os.path.exists(abs_path):
                return Response(status=404)

            return FileResponse(path=abs_path)

        return TemplateResponse(
            name='lona/bucket.html',
            context={
                'bucket': bucket,
            },
        )

        # bad request
        return Response(status=400)

    def on_view_cleanup(self, data):
        Bucket._close_buckets(request=data.request)
