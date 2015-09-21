#!/usr/bin/env python

from distutils.core import setup

setup(name='minimalisp',
    version='1.0',
    description='An implementation of a small lisp language',
    author='Joe Jordan',
    author_email='tehwalrus@h2j9k.org',
    url='https://github.com/joe-jordan/minimalisp',
    packages=['minimalisp'],
    scripts=['scripts/minimalisp'],
    include_package_data=True
)
