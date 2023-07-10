from __future__ import annotations

from tempfile import TemporaryDirectory
from argparse import Namespace
from typing import List
import os

TEST_PROJECT_PATH = os.path.join(
    os.path.dirname(__file__),
    '../test_project',
)


def _generate_command_line_args(
        destination: str,
        clean: bool = False,
        static_dirs: List[str] | None = None,
) -> Namespace:

    namespace = Namespace(

        # basic configuration
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
        settings_pre_overrides={},
        settings_post_overrides={},
        debug_mode='',
        log_level='info',
        loggers=[],
        syslog_priorities='auto',

        # collect-static specific arguments
        destination=destination,
        clean=clean,
        silent=False,
        dry_run=False,
    )

    if static_dirs:
        namespace.settings_post_overrides['STATIC_DIRS'] = static_dirs

    return namespace


def _check_javascript_client_src_files(destination: str) -> None:
    import lona

    CLIENT_ROOT = os.path.join(
        os.path.dirname(lona.__file__),
        'client/_lona/client/',
    )

    for client_src_file in os.listdir(CLIENT_ROOT):
        abs_path = os.path.join(destination, '_lona/client/', client_src_file)

        # check existence
        assert os.path.exists(abs_path)

        # check content
        original = open(os.path.join(CLIENT_ROOT, client_src_file), 'r').read()
        copy = open(abs_path, 'r').read()

        assert copy == original


def _check_test_project_static_files(destination: str):

    # files in test_project/static
    static_root = os.path.join(TEST_PROJECT_PATH, 'static')

    for static_file in os.listdir(static_root):
        abs_path = os.path.join(destination, static_file)

        # check existence
        assert os.path.exists(abs_path)

        # check content
        original = open(os.path.join(static_root, static_file), 'r').read()
        copy = open(abs_path, 'r').read()

        assert copy == original

    # files defined in View.STATIC_FILES and AbstractNode.STATIC_FILES
    static_files = [

        # contains: (original_path, copy_path, )
        (os.path.join(TEST_PROJECT_PATH, 'views/frontend/node-styles.css'),
         os.path.join(destination, 'node-styles.css')),
        (os.path.join(TEST_PROJECT_PATH, 'views/frontend/view-styles.css'),
         os.path.join(destination, 'view-styles.css')),
    ]

    for original_path, copy_path in static_files:

        # check existence
        assert os.path.exists(copy_path)

        # check content
        original = open(original_path, 'r').read()
        copy = open(copy_path, 'r').read()

        assert copy == original


# tests #######################################################################
def test_basic_collect_static():
    from lona.command_line.collect_static import collect_static

    with TemporaryDirectory() as tmp_dir:
        args = _generate_command_line_args(
            destination=tmp_dir,
        )

        collect_static(args=args)

        _check_javascript_client_src_files(destination=tmp_dir)
        _check_test_project_static_files(destination=tmp_dir)


def test_non_empty_destinations():
    from lona.command_line.collect_static import collect_static

    with TemporaryDirectory() as tmp_dir:

        # create a file so the destination is not empty
        test_file_path = os.path.join(tmp_dir, 'foo.txt')

        with open(test_file_path, 'w+') as f:
            f.write('foo')

        # first run
        args = _generate_command_line_args(
            destination=tmp_dir,
            clean=False,
        )

        collect_static(args=args)

        assert os.path.exists(test_file_path)
        _check_javascript_client_src_files(destination=tmp_dir)
        _check_test_project_static_files(destination=tmp_dir)

        # second run
        args = _generate_command_line_args(
            destination=tmp_dir,
            clean=True,
        )

        collect_static(args=args)

        assert not os.path.exists(test_file_path)
        _check_javascript_client_src_files(destination=tmp_dir)
        _check_test_project_static_files(destination=tmp_dir)


def test_overlapping_directories():
    """
    This test tests the handling of overlapping directories.

    If a project has two static directories, containing overlapping paths,
    the collect-static mechanism should override reoccurring paths.

    Example:

        Static Directory 1
            /directory/file1.txt          <- should be present in the output
            /directory/file2.txt          <- should be overridden in the output

        Static Directory 2
            /directory/file2.txt          <- should be present in the output
    """

    from lona.command_line.collect_static import collect_static

    static_dir1 = TemporaryDirectory()
    static_dir2 = TemporaryDirectory()
    destination = TemporaryDirectory()

    # setup tmp_dir1
    os.makedirs(os.path.join(static_dir1.name, 'test-directory'))

    path = os.path.join(static_dir1.name, 'test-directory/file1.txt')

    with open(path, 'w+') as f:
        f.write('tmp_dir1')

    path = os.path.join(static_dir1.name, 'test-directory/file2.txt')

    with open(path, 'w+') as f:
        f.write('tmp_dir1')

    # setup tmp_dir2
    os.makedirs(os.path.join(static_dir2.name, 'test-directory'))

    path = os.path.join(static_dir2.name, 'test-directory/file2.txt')

    with open(path, 'w+') as f:
        f.write('tmp_dir2')

    # run collect static
    args = _generate_command_line_args(
        static_dirs=[
            static_dir1.name,
            static_dir2.name,
        ],
        destination=destination.name,
        clean=False,
    )

    collect_static(args=args)

    # run checks
    file1 = os.path.join(destination.name, 'test-directory/file1.txt')
    file2 = os.path.join(destination.name, 'test-directory/file2.txt')

    assert os.path.exists(file1)
    assert os.path.exists(file2)

    file1_content = open(file1, 'r').read()
    file2_content = open(file2, 'r').read()

    assert file1_content == 'tmp_dir1'
    assert file2_content == 'tmp_dir1'


def test_deeply_nested_directories():
    from lona.command_line.collect_static import collect_static

    # setup temp dir
    static_dir = TemporaryDirectory()
    destination = TemporaryDirectory()

    parent_dir = os.path.join(static_dir.name, 'a/b/c')
    static_file = os.path.join(parent_dir, 'file.txt')

    os.makedirs(parent_dir)

    with open(static_file, 'w+') as f:
        f.write('file.txt')

    # run collect static
    args = _generate_command_line_args(
        static_dirs=[
            static_dir.name,
        ],
        destination=destination.name,
        clean=False,
    )

    collect_static(args=args)

    # run checks
    static_file = os.path.join(destination.name, 'a/b/c/file.txt')

    assert os.path.exists(static_file)


def test_deeply_nested_static_file_paths():
    from lona.command_line.collect_static import collect_static
    from lona.static_files import StaticFile
    from lona.html import Node

    class TestNode(Node):
        STATIC_FILES = [
            StaticFile(
                name='static-file-1.txt',
                path='static/static-file-1.txt',
                url='static-file-1.txt',
            ),
            StaticFile(
                name='static-file-2.txt',
                path='static/a/b/c/static-file-2.txt',
                url='a/b/c/static-file-2.txt',
            ),
        ]

    # setup temp dir
    destination = TemporaryDirectory()

    # run collect static
    args = _generate_command_line_args(
        destination=destination.name,
        clean=False,
    )

    collect_static(args=args)

    # run checks
    static_file_1 = os.path.join(destination.name, 'static-file-1.txt')
    static_file_2 = os.path.join(destination.name, 'a/b/c/static-file-2.txt')

    assert os.path.exists(static_file_1)
    assert os.path.exists(static_file_2)
