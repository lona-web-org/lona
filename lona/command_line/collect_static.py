import shutil
import os

from aiohttp.web import Application

from lona.logging import setup_logging
from lona.server import LonaServer


def collect_static(args):
    def _print(*print_args, **print_kwargs):
        if args.silent:
            return

        print(*print_args, **print_kwargs)

    def _rm(path):
        _print('rm -rf {}'.format(path))

        if args.dry_run:
            return

        if os.path.isdir(path):
            shutil.rmtree(path)

        else:
            os.unlink(path)

    def _mkdir(path):
        _print('mkdir -p {}'.format(path))

        if args.dry_run:
            return

        try:
            os.makedirs(path)

        except FileExistsError:
            pass

    def _cp(source, destination):
        source_is_dir = os.path.isdir(source)

        if source_is_dir:
            _print('cp -r {} {}'.format(source, destination))

        else:
            _print('cp {} {}'.format(source, destination))

        if args.dry_run:
            return

        if source_is_dir:
            shutil.copytree(source, destination)

        else:
            shutil.copy(source, destination)

    # setup logging
    setup_logging(args)

    # setup server
    server = LonaServer(
        app=Application(),
        project_root=args.project_root,
        settings_paths=args.settings,
        settings_pre_overrides=args.settings_pre_overrides,
        settings_post_overrides=args.settings_post_overrides,
    )

    # check destination
    if not os.path.exists(args.destination):
        exit("'{}' does not exist".format(args.destination))

    if not os.path.isdir(args.destination):
        exit("'{}' is no directory".format(args.destination))

    # clean
    if args.clean:
        for name in os.listdir(args.destination):
            path = os.path.join(args.destination, name)
            _rm(path)

    # copy node static files
    for static_file in server.static_file_loader.static_files[::-1]:
        if not static_file.enabled:
            continue

        destination = os.path.join(
            args.destination,
            static_file.url,
        )

        _cp(static_file.path, destination)

    # copy static files from static directories
    for static_dir in server.static_file_loader.static_dirs[::-1]:
        for name in os.listdir(static_dir):
            source = os.path.join(static_dir, name)
            destination = os.path.join(args.destination, name)

            _cp(source, destination)

    # copy client
    client_url = server.settings.STATIC_FILES_CLIENT_URL

    if client_url.startswith('/'):
        client_url = client_url[1:]

    destination = os.path.join(
        args.destination,
        client_url,
    )

    _mkdir(os.path.dirname(destination))
    _cp(server.client_pre_compiler.resolve(), destination)
