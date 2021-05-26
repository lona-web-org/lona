import pytest


@pytest.mark.dependency(depends=[
    'tests/test_html_attribute_list.py::test_attribute_list',
], scope='session')
def test_node_api():
    pass
