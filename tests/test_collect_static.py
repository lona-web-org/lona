from tempfile import TemporaryDirectory
from argparse import Namespace
import os

TEST_PROJECT_PATH = os.path.join(
    os.path.dirname(__file__),
    '../test_project',
)


def _generate_command_line_args(
        destination: str,
        clean: bool = False,
) -> Namespace:

    return Namespace(

        # basic configuration
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
        settings_pre_overrides=[],
        settings_post_overrides=[],
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


def _check_javascript_client_src_files(destination: str) -> None:
    import lona

    CLIENT_ROOT = os.path.join(
        os.path.dirname(lona.__file__),
        'client/_lona',
    )

    for client_src_file in os.listdir(CLIENT_ROOT):
        abs_path = os.path.join(destination, '_lona/', client_src_file)

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

    # files defined in LonaView.STATIC_FILES and AbstractNode.STATIC_FILES
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
