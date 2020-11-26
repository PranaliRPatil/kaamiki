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
Kaamiki Files

An utility for file create and read-write operations in Kaamiki.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from kaamiki import Neo
from kaamiki.utils import exceptions

# Exclude excel based files as the protocol that these files use for
# reading and writing is totally different than usual. Also for now
# kaamiki is not having an scope for handling data from these files.
_UNSUPPORTED_FILETYPES = [".xlsx", ".xlsm", "xlsb"]

# All file modes except `bytes` and its derivatives aren't supported.
_SUPPORTED_FILEMODES = ["r", "w", "a", "r+", "w+", "a+", "t", "x"]

_CRLF = "\r\n"


class File(object, metaclass=Neo):
  """
  A TextIOWrapper that handles file related operations.

  File provides an interface for creating, reading and writing files
  on/from/to the local disks.
  """

  def __init__(self,
               file_path: Union[Path, str],
               mode: str,
               encoding: Optional[str] = None,
               buffering: int = -1,
               max_bytes: int = 0,
               max_lines: int = 0,
               **kwargs: Any) -> None:
    """Initialize file with rotation parameters."""
    file_path = Path(file_path)
    self.file_path = file_path.absolute()
    if self.suffix in _UNSUPPORTED_FILETYPES:
      raise exceptions.UnsupportedFileType(suffix=self.suffix, valid=True)
    if mode not in _SUPPORTED_FILEMODES or "b" in mode:
      raise NotImplementedError(f"{mode!r} mode is not supported by File")
    if max_bytes > 0 or max_lines > 0:
      # If rotation or rollover is wanted, it makes no sense to use
      # another mode than `a`. If for example `w` were specified, then
      # if there were multiple runs of the calling application, the
      # files from previous runs would be lost if the `w` is respected,
      # because the file would be truncated on each run.
      mode = "a"
    self.mode = mode
    self.is_writable = mode in ("w", "w+", "a", "a+", "r+")
    self.is_readable = mode in ("r", "r+", "w+", "a+")
    self.encoding = encoding
    self.buffering = buffering
    self.max_bytes = max_bytes
    self.max_lines = max_lines
    self.kwargs = kwargs
    self.idx = self.index
    self.file = None
    self.closed = False
    self.open()
    self.rotate()

  def __enter__(self) -> "File":
    """Allow File to be used with `with` statement."""
    return self

  def __exit__(self, *args) -> None:
    """Allow File to be used with `with` statement."""
    self.close()

  @property
  def parent(self) -> Path:
    """Return parent directory of the file."""
    return self.file_path.parent

  @property
  def name(self) -> str:
    """Return name of the file with extension."""
    return self.file_path.name

  @property
  def stem(self) -> str:
    """Return name of the file without extension."""
    return self.file_path.stem

  @property
  def suffix(self) -> str:
    """Return extension of the file."""
    return self.file_path.suffix

  @property
  def size(self) -> int:
    """Return size of the file in bytes."""
    return self.file_path.stat().st_size

  @property
  def index(self) -> int:
    """Return count of files with same name."""
    return len(fnmatch.filter(os.listdir(self.parent), f"{self.name}*.?"))

  @property
  def create(self) -> None:
    """Create an empty file if it doesn't exists."""
    if self.file_path.exists():
      self.file_path.touch()

  def open(self) -> None:
    """Open file for read-write operation."""
    self.file = open(self.file_path, self.mode, self.buffering, self.encoding)
    self.closed = False

  def flush(self) -> None:
    """
    Flush the writable file.

    Flushing stream ensures that the data has been cleared from the
    internal buffer without any guarantee on whether its written to the
    local disk.
    This means that the data would survive an application crash but not
    necessarily an OS crash.
    """
    if self.closed:
      raise exceptions.FileAlreadyClosed(file=self.name, valid=True)
    if self.is_writable:
      self.file.flush()

  def close(self) -> None:
    """Close file post IO operation."""
    self.file.close()
    self.closed = True

  def rotate(self) -> None:
    """
    Rotate file as needed.

    Rotate file if the current file in use reaches a particular size or
    has written enough lines to rollover to a new file.
    """
    _rotate = False
    if self.max_bytes > 0:
      if self.size > self.max_bytes:
        _rotate = True
    if _rotate:
      self.close()
      os.rename(self.file_path, f"{self.file_path}.{self.idx}")
      self.idx += 1
      self.open()

  def write(self,
            *args: Sequence[Any],
            new_line: bool = True) -> None:
    if not self.is_writable:
      raise exceptions.PermissionDeniedError(self.name, self.mode, valid=True)
    if self.closed:
      raise exceptions.FileAlreadyClosed(file=self.name, valid=True)
    raw = list(map(lambda x: "" if x is None else str(x), args))
    self.file.write(" ".join(raw) + _CRLF if new_line else "")
    self.flush()
    self.rotate()
