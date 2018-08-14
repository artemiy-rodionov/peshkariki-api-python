#!/usr/bin/env python
import io
import re
from collections import OrderedDict

from setuptools import setup

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('flask/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='Peshkariki',
    version=version,
    url='https://github.com/artemiy-rodionov/peshkariki-api-python',
    project_urls=OrderedDict((
        ('Code', 'https://github.com/artemiy-rodionov/peshkariki-api-python'),
    )),
    license='BSD',
    author='Artemiy Rodionov',
    author_email='artemiy.rodionov@gmail.com',
    maintainer='Artemiy Rodionov',
    maintainer_email='artemiy.rodionov@gmail.com',
    description='An api client for peshkariki.ru.',
    long_description=readme,
    packages=['peshkariki'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires=',!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'requests>=2',
    ],
    extras_require={
        'dev': [
            'pytest>=3',
            'coverage',
            'tox',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    )
