#!/usr/bin/env python
# # coding: utf-8

from setuptools import setup
long_description = open('README').read()


setup(
    name='pyrally',
    description='Rally API Client',
    long_description=long_description,
    version='0.3.4.1',
    author='Alex Couper',
    author_email='amcouper@gmail.com',
    url='https://github.com/alexcouper/pyrally',
    packages=['pyrally'],
    install_requires=['simplejson'],
    zip_safe=True,
    scripts=[
    ],
    package_data={
        '': ['*.txt', '*.rst'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
