import pytest


@pytest.mark.dependency(depends=[
    'tests/test_0001_html.py::test_attribute_dict',
    'tests/test_0001_html.py::test_attribute_list',
], scope='session')
def test_node_api():
    pass
