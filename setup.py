#!/usr/bin/env python

from os.path import join, dirname

from setuptools import setup, find_packages

here = dirname(__file__)

setup(
    name='bitmake',
    version='1.0.0',
    description="Official python3 BitMake exchange API",
    long_description=open(join(here, 'README.md')).read(),
    long_description_content_type='text/markdown',
    license='MIT',
    author='bitmake',
    author_email='python-sdk@bitmake.com',
    # url='',
    # download_url='',
    install_requires=['requests', 'websockets'],
    packages=find_packages(),
    keywords=[
        'bitmake', 'exchange-api', 'crypto-exchange', 'digital-currency', 'trading'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
)

# PyPi publish flow
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*
