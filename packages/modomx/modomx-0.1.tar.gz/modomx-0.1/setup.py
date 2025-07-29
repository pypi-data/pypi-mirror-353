# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='modomx',
    version='0.1',
    description='Omxplayer wrapper compatible with Python 2.x',
    author='Marcelo Prestes',
    author_email='marcelo.prestes@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    python_requires='>=2.7, <3',
)

