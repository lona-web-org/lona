from tempfile import TemporaryDirectory
import string
import random
import uuid
import os

from playwright.async_api import async_playwright
import aiohttp

from lona.pytest import eventually
from lona import Bucket, View


async def test_buckets(lona_app_context):

    # test state
    upload_temp_dir = TemporaryDirectory()
    download_temp_dir = TemporaryDirectory()

    bucket_objects = []
    bucket_count = [1]
    bucket_kwargs = {}
    added_files = []
    deleted_files = []

    # lona view setup
    def setup_app(app):

        @app.route('/')
        class BucketView(View):
            def on_add(self, files):
                added_files.extend(files)

                self.show('ON_ADD')

            def on_delete(self, files):
                deleted_files.extend(files)

                self.show('ON_DELETE')

            def handle_request(self, request):
                bucket_objects.clear()

                for _ in range(bucket_count[0]):
                    bucket_objects.append(
                        Bucket(
                            request=request,
                            on_add=self.on_add,
                            on_delete=self.on_delete,
                            **bucket_kwargs,
                        ),
                    )

                return 'BUCKETS SETUP'

    context = await lona_app_context(setup_app)
    url = context.make_url('/')

    # helper
    def get_bucket(index=0):
        return bucket_objects[index]

    def generate_file(size=256):
        file_name = f'{uuid.uuid1()}.txt'
        file_path = os.path.join(upload_temp_dir.name, file_name)

        with open(file_path, 'w+') as handle:
            for _ in range(size):
                handle.write(random.choice(string.ascii_letters))

        return file_name, file_path

    def compare_files(path_a, path_b):
        return open(path_a, 'r').read() == open(path_b, 'r').read()

    async def setup_buckets(
            page,
            count=1,
            index=True,
            max_files=None,
            max_size=None,
    ):

        bucket_count[0] = count

        bucket_kwargs.update({
            'index': index,
            'max_files': max_files,
            'max_size': max_size,
        })

        await page.goto(url)
        await page.wait_for_selector('#lona:has-text("BUCKETS SETUP")')

        added_files.clear()
        added_files.clear()

    async def close_buckets(page):
        await page.goto('about:blank')

    async def files_added(page):
        await page.wait_for_selector('#lona:has-text("ON_ADD")')

    async def files_deleted(page):
        await page.wait_for_selector('#lona:has-text("ON_DELETE")')

    async def upload_files(*files, index=0, extra_data=None):
        data = {}
        url = context.make_url(get_bucket(index=index).get_add_url())

        for file_name, file_path in files:
            data[file_name] = open(file_path, 'rb')

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=url,
                data={
                    **data,
                    **(extra_data or {}),
                },
            )

            return response

    async def get_index(index=0):
        url = context.make_url(get_bucket(index=index).get_url())

        async with aiohttp.ClientSession() as session:
            return (await session.get(url))

    async def download_file(file_name, index=0):
        url = context.make_url(
            get_bucket(index=index).get_url(file_name=file_name),
        )

        file_path = os.path.join(download_temp_dir.name, file_name)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

            if not response.status == 200:
                return response, '', ''

            with open(file_path, 'wb') as fd:
                async for chunk in response.content.iter_chunked(8):
                    fd.write(chunk)

            return response, file_name, file_path

    async def delete_file(file_name, index=0):
        url = context.make_url(get_bucket(index=index).get_delete_url())

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=url,
                data={
                    'name': file_name,
                },
            )

            return response

    # test code
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # add files ###########################################################
        await setup_buckets(page)

        # upload files
        file_name_1, file_path_1 = generate_file(size=100)
        file_name_2, file_path_2 = generate_file(size=50)

        response = await upload_files(
            (file_name_1, file_path_1),
            (file_name_2, file_path_2),
        )

        assert response.status == 200

        await files_added(page)

        # check hooks
        assert sorted(added_files) == sorted([file_name_1, file_name_2])
        assert deleted_files == []

        # check uploaded files
        assert compare_files(file_path_1, get_bucket().get_path(file_name_1))
        assert compare_files(file_path_2, get_bucket().get_path(file_name_2))

        assert (
            sorted([file_name_1, file_name_2]) ==
            sorted(get_bucket().get_file_names())
        )

        # index ###############################################################
        response = await get_index()
        response_text = await response.text()

        assert response.status == 200
        assert file_name_1 in response_text
        assert file_name_2 in response_text

        # get files ###########################################################
        # file 1
        result = await download_file(file_name_1)
        response, download_file_name_1, download_file_path_1 = result

        assert response.status == 200
        assert compare_files(file_path_1, download_file_path_1)

        # file 2
        result = await download_file(file_name_2)
        response, download_file_name_2, download_file_path_2 = result

        assert response.status == 200
        assert compare_files(file_path_2, download_file_path_2)

        # file not found
        result = await download_file('unknown-file.txt')
        response, download_file_name_2, download_file_path_2 = result

        assert response.status == 404

        # delete files ########################################################
        response = await delete_file(file_name_1)

        assert response.status == 200

        await files_deleted(page)

        assert not os.path.exists(get_bucket().get_path(file_name_1))
        assert os.path.exists(get_bucket().get_path(file_name_2))

        # cleanup #############################################################
        await close_buckets(page)

        for attempt in eventually():
            async with attempt:
                assert not os.path.exists(get_bucket().get_path())

        # max files ###########################################################
        # too many files in one request
        await setup_buckets(page, max_files=2)

        file_name_1, file_path_1 = generate_file(size=8)
        file_name_2, file_path_2 = generate_file(size=8)
        file_name_3, file_path_3 = generate_file(size=8)

        response = await upload_files(
            (file_name_1, file_path_1),
            (file_name_2, file_path_2),
            (file_name_3, file_path_3),
        )

        assert response.status == 400

        assert not os.path.exists(get_bucket().get_path(file_name_1))
        assert not os.path.exists(get_bucket().get_path(file_name_2))
        assert not os.path.exists(get_bucket().get_path(file_name_3))

        await close_buckets(page)

        # too many files in two requests
        await setup_buckets(page, max_files=2)

        file_name_1, file_path_1 = generate_file(size=8)
        file_name_2, file_path_2 = generate_file(size=8)

        response = await upload_files(
            (file_name_1, file_path_1),
            (file_name_2, file_path_2),
        )

        assert response.status == 200

        file_name_3, file_path_3 = generate_file(size=8)

        response = await upload_files(
            (file_name_3, file_path_3),
        )

        assert response.status == 400

        assert os.path.exists(get_bucket().get_path(file_name_1))
        assert os.path.exists(get_bucket().get_path(file_name_2))
        assert not os.path.exists(get_bucket().get_path(file_name_3))

        await close_buckets(page)

        # max size ############################################################
        # too much data in one request
        await setup_buckets(page, max_size=100)

        file_name_1, file_path_1 = generate_file(size=50)
        file_name_2, file_path_2 = generate_file(size=50)
        file_name_3, file_path_3 = generate_file(size=50)

        response = await upload_files(
            (file_name_1, file_path_1),
            (file_name_2, file_path_2),
            (file_name_3, file_path_3),
        )

        assert response.status == 400

        assert not os.path.exists(get_bucket().get_path(file_name_1))
        assert not os.path.exists(get_bucket().get_path(file_name_2))
        assert not os.path.exists(get_bucket().get_path(file_name_3))

        await close_buckets(page)

        # too much files in two requests
        await setup_buckets(page, max_size=100)

        file_name_1, file_path_1 = generate_file(size=50)
        file_name_2, file_path_2 = generate_file(size=50)

        response = await upload_files(
            (file_name_1, file_path_1),
            (file_name_2, file_path_2),
        )

        assert response.status == 200

        file_name_3, file_path_3 = generate_file(size=50)

        response = await upload_files(
            (file_name_3, file_path_3),
        )

        assert response.status == 400

        assert os.path.exists(get_bucket().get_path(file_name_1))
        assert os.path.exists(get_bucket().get_path(file_name_2))
        assert not os.path.exists(get_bucket().get_path(file_name_3))

        await close_buckets(page)

        # mixed post ##########################################################
        await setup_buckets(page)

        # upload files
        file_name_1, file_path_1 = generate_file(size=8)

        response = await upload_files(
            (file_name_1, file_path_1),
            extra_data={
                'foo': 'bar',
            },
        )

        assert response.status == 200

        await files_added(page)

        assert compare_files(file_path_1, get_bucket().get_path(file_name_1))

        await close_buckets(page)

        # multiple buckets ####################################################
        await setup_buckets(page, count=2)

        file_name_1, file_path_1 = generate_file(size=8)
        file_name_2, file_path_2 = generate_file(size=8)

        await upload_files((file_name_1, file_path_1), index=0)
        await upload_files((file_name_2, file_path_2), index=1)

        for attempt in eventually():
            async with attempt:
                assert os.path.exists(get_bucket(0).get_path(file_name_1))
                assert not os.path.exists(get_bucket(0).get_path(file_name_2))

                assert not os.path.exists(get_bucket(1).get_path(file_name_1))
                assert os.path.exists(get_bucket(1).get_path(file_name_2))

        await close_buckets(page)

        for attempt in eventually():
            async with attempt:
                assert not os.path.exists(get_bucket(0).get_path(file_name_1))
                assert not os.path.exists(get_bucket(0).get_path(file_name_2))

                assert not os.path.exists(get_bucket(1).get_path(file_name_1))
                assert not os.path.exists(get_bucket(1).get_path(file_name_2))

        # disabled index ######################################################
        await setup_buckets(page, index=False)

        file_name_1, file_path_1 = generate_file(size=8)

        response = await upload_files(
            (file_name_1, file_path_1),
        )

        # index
        response = await get_index()

        assert response.status == 401

        # get file
        result = await download_file(file_name_1)
        response, download_file_name_1, download_file_path_1 = result

        assert response.status == 401
        assert not download_file_path_1

        await close_buckets(page)
