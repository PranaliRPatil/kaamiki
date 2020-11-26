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

Kaamiki is a simple machine learning framework for obvious tasks. It is
an operating system agnostic AI* developing package which aims at
providing high-level and flexible python abstractions for running simple
machine learning codes with great ease. Kaamiki also offers a couple of
simple python based nifty tools (logger, file handlers, etc.) which
could rather provide an extension to the developers existing work.
"""

import getpass
import json
import re
import string
import urllib.error
import urllib.request
from distutils.version import StrictVersion
from pathlib import Path
from threading import Lock

from pkg_resources import parse_version

__name__ = "kaamiki"
__version__ = "0.0.1"
__author__ = "Kaamiki Development Team"

__all__ = ["BASE_DIR", "SESSION_USER", "Neo", "replace_chars", "show_version"]

# Base directory which is used for caching, logging and storing details
# and data generated for/of a kaamiki session. Making any modifications
# to the `BASE_DIR` can cause issues as all the session related events,
# logs and data are stored in this directory.
BASE_DIR = Path().home() / f".{__name__}"

_DEFAULT_SEPARATOR = "_"


class Neo(type):
  """
  An implementation of thread-safe Singleton design pattern.

  Singleton is a creational design pattern, which ensures that only a
  single object of its kind exist and provides a single point of access
  to it for any other code. The below is a thread-safe implementation of
  the Singleton design pattern. You can instantiate a class multiple
  times and yet you would get reference to the same object.

  See https://stackoverflow.com/q/6760685 for more methods of
  implementing singletons in code.

  Example:
    >>> from kaamiki import Neo
    >>>
    >>> class DummyClass(metaclass=Neo):
    ...     pass
    ...
    >>> singleton_obj1 = DummyClass()
    >>> singleton_obj2 = DummyClass()
    >>> singleton_obj1
    <__main__.DummyClass object at 0x7fc8f1948970>
    >>> singleton_obj2
    <__main__.DummyClass object at 0x7fc8f1948970>
  """
  # For better understanding of the below implementation, read this:
  # https://refactoring.guru/design-patterns/singleton/python/example
  _instances = {}
  _lock = Lock()

  def __call__(cls, *args, **kwargs):
    """Callable instance of Neo."""
    with cls._lock:
      if cls not in cls._instances:
        cls._instances[cls] = super().__call__(*args, **kwargs)
    return cls._instances[cls]


def replace_chars(text: str, sub: str = _DEFAULT_SEPARATOR) -> str:
  """Replace special characters with substitution string."""
  # See https://stackoverflow.com/a/23996414/14316408 for more help.
  return re.sub(r"[" + re.escape(string.punctuation) + "]", sub, text).lower()


def latest_version() -> str:
  """Check for the latest stable version of kaamiki on PyPI."""
  try:
    PYPI_URL = f"https://pypi.org/pypi/{__name__}/json"
    data = json.load(urllib.request.urlopen(PYPI_URL))["releases"].keys()
    version = sorted(data, key=StrictVersion, reverse=True)[0]
    return version if version else __version__
  except urllib.error.URLError:
    # Explicitly return a custom error string in case the network is not
    # available while checking the state on PyPI.
    return "NetworkConnectionError"


def show_version() -> None:
  """
  Show version status of kaamiki.

  Show the installed version status of kaamiki with respect to the
  available builds. This function not only displays the installed build
  but displays the upgrade or downgrade recommendations when checked.
  """
  latest = latest_version()
  pkg = __name__.capitalize()
  if latest != "NetworkConnectionError":
    if parse_version(__version__) < parse_version(latest):
      print(f"You are using an older version of {pkg}, v{__version__}\n"
            f"However, v{latest} is currently available for download. You "
            f"should consider upgrading to it using \"pip install --upgrade "
            f"{__name__}\" command.")
    elif parse_version(__version__) > parse_version(latest):
      print(f"You are using a development version of {pkg}, v{__version__}\n"
            f"If you want to roll back to a stable version, consider "
            f"downgrading using \"pip install {__name__}\" command.")
    else:
      print(f"You are using the latest stable version of {pkg}, v{latest}")
  else:
    print(f"WARNING: Internet connection is questionable at the moment. "
          f"Couldn't check for the latest stable version of {pkg}.\nInstalled "
          f"version is v{__version__}")


SESSION_USER = replace_chars(getpass.getuser())