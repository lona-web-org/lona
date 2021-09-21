#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from lona import VERSION_STRING

setup(
    include_package_data=True,
    name='lona',
    version=VERSION_STRING,
    author='Florian Scherf',
    url='https://github.com/lona-web-org/lona',
    author_email='f.scherf@pengutronix.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3,<4',
        'jinja2',
        'rlpython',
        'typing-extensions',
    ],
    scripts=[
        'bin/lona',
    ],
    entry_points={
        'pytest11': [
            'lona = lona.pytest',
        ],
    },
)
