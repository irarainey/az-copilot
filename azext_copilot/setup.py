#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1.0'

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

setup(
    name='copilot',
    version=VERSION,
    description='Azure CLI Copilot Extension',
    author='Ira Rainey',
    author_email='ira.rainey@microsoft.com',
    url='https://github.com/irarainey/azure-cli-copilot',
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_copilot': ['azext_metadata.json']},
)
