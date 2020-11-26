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

Kaamiki is a simple machine learning framework for obvious tasks.
"""
# TODO(xames3): Add a descriptive docstring which would help the users
# and developers alike to get an idea what and how kaamiki could assist
# them right out of the box with minimal efforts.

import os
import sys

# Raise exceptions if the host system is not properly configured
# for installing kaamiki. See https://github.com/kaamiki/kaamiki
# for more help.
if sys.version_info < (3, ):
  sys.exit("Python 2 has officially reached end-of-life and is no longer "
           "supported by Kaamiki.")

if sys.version_info < (3, 6, 9):
  sys.exit("Kaamiki supports minimum python 3.6.9 and above. Kindly upgrade "
           "your python interpreter to a suitable version.")

if os.name == "nt" and sys.maxsize.bit_length() == 31:
  sys.exit("32-bit Python runtime is not supported. Please switch to 64-bit "
           "Python.")

from setuptools import find_packages, setup

from kaamiki import BASE_DIR, __author__, __name__, __version__

# Flag which raises warning if the installed version of kaamiki is
# either outdated or a nightly (development) build.
STATUS = 0

DESCRIPTION = __doc__.splitlines()[3]


def parse_readme() -> str:
  """Parse README.md for long description of kaamiki."""
  with open("README.md", "r") as file:
    return file.read()


with open("requirements.txt", "r") as requirements:
  if os.name == "nt":
    packages = [idx for idx in requirements]
  else:
    skip = ["pywin32", "pypywin32", "pywinauto"]
    packages = [idx for idx in requirements if idx.rstrip() not in skip]

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    author_email="xames3.kaamiki@gmail.com",
    maintainer_email="xames3.kaamiki@gmail.com",
    url="https://github.com/kaamiki/kaamiki",
    license="Apache Software License 2.0",
    description=DESCRIPTION,
    long_description=parse_readme(),
    long_description_content_type="text/markdown",
    keywords="kaamiki python",
    zip_safe=False,
    install_requires=packages,
    python_requires=">=3.6.9",
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "kaamiki = kaamiki.parser:main",
        ],
    },
    # You can find the complete list here:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Home Automation",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

# Create base directory for caching, logging and storing data for/of
# a kaamiki session.
if not BASE_DIR.exists():
  os.mkdir(BASE_DIR)
with open(BASE_DIR / "update", "w") as update:
  # TODO(xames3): Check if the status is really necessary with the team.
  update.write(f"name: {__name__}\n"
               f"version: {__version__}\n"
               f"status: {STATUS}")