# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='modomx',
    version='0.1.1',  # Incremente a versão
    description='Omxplayer wrapper compatible with Python 2.x',
    long_description="Omxplayer wrapper compatible with Python 2.x",
    long_description_content_type="text/markdown",
    author='Marcelo Prestes',
    author_email='marcelo.prestes@gmail.com',
    url='https://github.com/mmprestes/modomx',  # Adicione se tiver
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',  # Adicione a licença
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7, <3',
)
