#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from lona import VERSION_STRING

setup(
    include_package_data=True,
    name='lona',
    version=VERSION_STRING,
    author='Florian Scherf',
    url='https://github.com/fscherf/lona',
    author_email='f.scherf@pengutronix.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.6.2',
        'jinja2',
    ],
    scripts=[
        'bin/lona',
    ],
)
