##############################################################################
#
# Copyright (c) 2006-2015 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

py_version = sys.version_info[:2]

if py_version < (2, 7):
    raise RuntimeError('On Python 2, Supervisor requires Python 2.7 or later')
elif (3, 0) < py_version < (3, 4):
    raise RuntimeError('On Python 3, Supervisor requires Python 3.4 or later')

# setuptools is required as a runtime dependency only on
# Python < 3.8.  See the comments in supervisor/compat.py.
requires = [
    "setuptools; python_version < '3.8'",
]

tests_require = []
testing_extras = tests_require + [
    'pytest',
    'pytest-cov',
    ]

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README_PYPI.rst'), 'r', encoding='utf-8') as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.rst'), 'r') as f:
        CHANGES = f.read()
except Exception:
    README = """\
Supervisor-TianHei-Enhanced is an enhanced version of the original Supervisor 
that allows its users to control a number of processes on UNIX-like operating systems.
This version includes additional features such as improved web interface with group operations,
enhanced log viewing with syntax highlighting, and other user experience improvements.

Based on the original Supervisor by Chris McDonough and contributors.
"""
    CHANGES = ''

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: No Input/Output (Daemon)',
    'Intended Audience :: System Administrators',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Topic :: System :: Boot',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

version_txt = os.path.join(here, 'supervisor/version.txt')
with open(version_txt, 'r') as f:
    supervisor_version = f.read().strip()

dist = setup(
    name='supervisor-tianhei-enhanced',
    version=supervisor_version,
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
    url='https://github.com/tianhei/supervisor-enhanced',
    project_urls={
        'Original Project': 'http://supervisord.org/',
        'Documentation': 'http://supervisord.org',
        'Issue Tracker': 'https://github.com/tianhei/supervisor-enhanced/issues',
        'Source': 'https://github.com/tianhei/supervisor-enhanced',
    },
    description="An enhanced version of Supervisor - A system for controlling process state under UNIX",
    long_description=README + '\n\n' + CHANGES,
    long_description_content_type='text/x-rst',
    classifiers=CLASSIFIERS,
    author="TianHei (Based on original work by Chris McDonough)",
    author_email="tianhei@example.com",
    maintainer="TianHei",
    maintainer_email="tianhei@example.com",
    packages=find_packages(),
    install_requires=requires,
    extras_require={
        'testing': testing_extras,
    },
    tests_require=tests_require,
    include_package_data=True,
    zip_safe=False,
    test_suite="supervisor.tests",
    entry_points={
        'console_scripts': [
            'supervisord = supervisor.supervisord:main',
            'supervisorctl = supervisor.supervisorctl:main',
            'echo_supervisord_conf = supervisor.confecho:main',
            'pidproxy = supervisor.pidproxy:main',
        ],
    },
    keywords='supervisor process control daemon monitoring enhanced',
)
