#!/usr/bin/env python

# -*-coding:utf-8 -*-

from setuptools import setup

setup(
    name='cuffnote',
    version='0.3.11',
    description='Modeling mortgage loan scenarios',
    url='https://github.com/bdowdell/cuffnote',
    author='Ben Dowdell',
    author_email='ben.dowdell87@gmail.com',
    license='MIT',
    packages=['cuffnote'],
    install_requires=['numpy', 'numpy-financial', 'pandas', 'matplotlib'],
    test_suite='tests',
    zip_safe=False,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)