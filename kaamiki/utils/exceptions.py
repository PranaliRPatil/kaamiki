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
Kaamiki Exceptions

Collection of all the exceptions raised by various kaamiki operations.
"""


def this_is_effing_bug() -> str:
  """Return bug report warning."""
  title = "YIKES! There's a bug:"
  title += "".join(["\n", "-" * len(title)])
  return ("\n\n{}\nIf you are seeing this, then there is something wrong with "
          "Kaamiki and not your code.\nPlease report this issue immediately "
          "here: \"https://github.com/kaamiki/kaamiki/issues/new\"\nso that "
          "we can fix the issue at the earliest. It would be a great help if "
          "you could provide\nthe steps, traceback information or even a "
          "sample code for reproducing this bug while\nsubmitting an issue."
          "\n").format(title)


class KaamikiError(Exception):
  """Base exception class for all kaamiki related exceptions."""

  def __init__(self, message: str, valid: bool = False, **kwargs) -> None:
    if not valid:
      message += this_is_effing_bug()
    super().__init__(message)
    self.message = message
    for key, value in kwargs.items():
      setattr(self, key, value)

  def __str__(self) -> str:
    return self.message.format(**vars(self))


class InvalidArgumentError(KaamikiError):
  """Exception to be raised when a wrong argument is passed."""

  def __init__(self,
               message: str = "{arg!r} is not a valid argument",
               **kwargs) -> None:
    super().__init__(message, **kwargs)


class UnsupportedFileType(KaamikiError):
  """Exception to be raised when dealing with unsupported file types."""

  def __init__(
          self,
          message: str = "File I/O operation not supported by {suffix!r} file",
          **kwargs):
    super().__init__(message, **kwargs)


class FileAlreadyClosed(KaamikiError):
  """Exception to be raised when closing an already closed file."""

  def __init__(self,
               message: str = "File {file!r} is already closed",
               **kwargs) -> None:
    super().__init__(message, **kwargs)


class PermissionDeniedError(KaamikiError):
  """Exception to be raised when permissions aren't provided to file."""

  def __init__(self,
               file_path: str,
               mode: str,
               **kwargs) -> None:
    action = "writing" if "r" in mode else "reading"
    message = f"{file_path!r} doesn't have enough permission for {action} file"
    super().__init__(message, **kwargs)
