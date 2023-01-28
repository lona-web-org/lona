from distutils.dir_util import copy_tree
import shutil
import sys
import os

from lona.logging import setup_logging
from lona.server import Server


def collect_static(args):
    def _print(*print_args, **print_kwargs):
        if args.silent:
            return

        print(*print_args, **print_kwargs)

    def _rm(path):
        _print(f'rm -rf {path}')

        if args.dry_run:
            return

        if os.path.isdir(path):
            shutil.rmtree(path)

        else:
            os.unlink(path)

    def _cp(source, destination):
        source_is_dir = os.path.isdir(source)

        if source_is_dir:
            _print(f'cp -r {source} {destination}')

        else:
            _print(f'cp {source} {destination}')

        if args.dry_run:
            return

        if source_is_dir:
            if sys.version_info < (3, 8):
                # TODO: remove after Python 3.7 got removed
                # this is necessary because the `dirs_exists_ok` flag in
                # shutil.copytree was added in Python 3.8

                for rel_source in os.listdir(source):
                    abs_source = os.path.join(source, rel_source)
                    abs_destination = os.path.join(destination, rel_source)

                    if os.path.isdir(abs_source):
                        if not os.path.exists(abs_destination):
                            os.makedirs(abs_destination)

                        copy_tree(
                            src=abs_source,
                            dst=abs_destination,
                        )

                    else:
                        if not os.path.exists(destination):
                            os.makedirs(destination)

                        shutil.copy(
                            src=abs_source,
                            dst=abs_destination,
                        )

            else:
                shutil.copytree(source, destination, dirs_exist_ok=True)

        else:
            shutil.copy(source, destination)

    # setup logging
    setup_logging(args)

    # setup server
    server = Server(
        project_root=args.project_root,
        settings_paths=args.settings,
        settings_pre_overrides=args.settings_pre_overrides,
        settings_post_overrides=args.settings_post_overrides,
    )

    # check destination
    if not os.path.exists(args.destination):
        exit(f"'{args.destination}' does not exist")

    if not os.path.isdir(args.destination):
        exit(f"'{args.destination}' is no directory")

    # clean
    if args.clean:
        for name in os.listdir(args.destination):
            path = os.path.join(args.destination, name)
            _rm(path)

    # copy files
    for path, url in server._static_file_loader.get_paths():
        destination = os.path.join(args.destination, url)

        _cp(path, destination)
