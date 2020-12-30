# Copyright (c) 2020 Kaamiki Development Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author(s):
#     xames3 <44119552+xames3@users.noreply.github.com>

"""
Kaamiki

A Python based implementation of kaamiki.

Kaamiki is a simple cross-platform automation framework for data
science and machine learning tasks. It is an operating system agnostic
Artificial Intelligence development package which provides high-level
and flexible python abstractions for running simple machine learning
applications.
Kaamiki also offers python based nifty tools such as logger, file I/O
related functions, etc. which provides an extension to the developers
existing work.
"""

import os
import sys

# Raise early exceptions if the host system is not properly configured
# for installing the framework.
# See https://github.com/kaamiki/kaamiki for more help.
if sys.version_info < (3, ):
    sys.exit('Python 2 has officially reached end-of-life and is no '
             'longer supported by Kaamiki. Please upgrade your python '
             'interpreter to Python 3.6.X or above.')

if sys.version_info < (3, 6, 9):
    sys.exit('Kaamiki supports minimum python 3.6.9 and above. Kindly '
             'upgrade your python interpreter to a suitable version.')

if os.name == 'nt' and sys.maxsize.bit_length() == 31:
    sys.exit('32-bit Python runtime is not supported. '
             'Please switch to 64-bit Python interpreter.')

from setuptools import find_packages, setup

from kaamiki.config import settings


def parse_readme() -> str:
    """Parse README.md for long description of kaamiki."""
    with open('README.md', 'r') as file:
        return file.read()


with open('requirements.txt', 'r') as requirements:
    if os.name == 'nt':
        packages = [idx for idx in requirements]
    else:
        skip = ['pywin32', 'pypywin32', 'pywinauto']
        packages = [idx for idx in requirements if idx.rstrip() not in skip]

setup(
    name=settings.MARK_ONE.lower(),
    version=settings.FRAMEWORK_VERSION,
    author=settings.AUTHOR,
    author_email=settings.AUTHOR_EMAIL,
    maintainer=settings.MAINTAINER,
    maintainer_email=settings.MAINTAINER_EMAIL,
    url=settings.FRAMEWORK_URL,
    license=settings.OSS_LICENSE,
    description=settings.SHORT_DESCRIPTION,
    long_description=parse_readme(),
    long_description_content_type='text/markdown',
    keywords='python kaamiki',
    zip_safe=False,
    install_requires=packages,
    python_requires='>=3.6.9',
    include_package_data=True,
    packages=find_packages(),
    # You can find the complete list here:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Home Automation',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)

