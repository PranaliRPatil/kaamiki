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
Kaamiki File

An utility for file create and read-write operations in Kaamiki.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from kaamiki import Neo
from kaamiki.utils import exceptions

# Exclude excel based files as the protocol these files use for
# reading and writing is totally different than usual. Also for now
# kaamiki is not having an scope for handling data from these sort of
# files.
_UNSUPPORTED_FILETYPES = (".xlsx", ".xlsm", "xlsb")

# All file modes except `bytes` and its derivatives aren't supported.
# This is to avoid the conflicts while using threading.
_SUPPORTED_FILEMODES = ("r", "w", "a", "r+", "w+", "a+", "t", "x")
_WRITABLE_MODES = ("w", "w+", "a", "a+", "r+")
_READABLE_MODES = ("r", "r+", "w+", "a+")

_CRLF = "\r\n"
_SEP = " "


class File(object, metaclass=Neo):
  """
  A TextIOWrapper that handles file related operations.

  File provides an interface for creating, reading and writing files
  on/from/to the local disks using native python syntax. This ensures
  that the contents to be written are written is properly to the file
  and the file is `rotated` when needed.

  `Rotation` or `Rollover` means switching the file writing process
  from one file to the next either when the current file reaches a
  certain size or writes enough number of lines. As said above the file
  rotation is possible using File, the behaviour is not enabled by
  default. When `rotation` or `rollover` is wanted, you can specify the
  `max_bytes` or the `max_lines` arguments. These take an integer input
  which determines the rotational limit. `Rotation` occurs whenever the
  current file is nearly `max_bytes` in size or `max_lines` in length.
  Kaamiki will successively write and rename new files with extensions
  ".1", ".2" etc. appended to it. For example, the file being written is
  "kaamiki.txt" - when it gets filled up, it is then closed and renamed
  to "kaamiki.txt.1" and then "kaamiki.txt.2" and so on.

  When rotation is not needed like while reading the file, the arguments
  `max_bytes` and `max_lines` are automatically set to 0. This is to
  avoid the file permission issues. File reading works similarly.
  Instead of reading lines it reads across the files with similar names.

  NOTE: Kaamiki File doesn't support for I/O of excel based files.

  Examples:
    >>> with File("/home/kaamiki/misc/kaamiki.txt", "w") as f:
    ...   f.write("This is how you use the File class using `with`")
    ... 
    >>> f = File("/home/kaamiki/misc/kaamiki.txt", "w")
    >>> f.write("This is how you use the File class without `with`")
    >>> f.close()
  """

  def __init__(self,
               file_path: Union[Path, str],
               mode: str,
               encoding: Optional[str] = None,
               buffering: int = -1,
               max_bytes: int = 0,
               max_lines: int = 0) -> None:
    """
    Initialize file

    Initialize file with default file-type parameters like file mode
    type, encoding and buffering. Non-default parameters like max_bytes
    and max_lines will decide whether the file is to be rotated or not
    when writing.
    """
    file_path = Path(file_path)
    self.file_path = file_path.absolute()
    if self.suffix in _UNSUPPORTED_FILETYPES:
      raise exceptions.UnsupportedFileType(suffix=self.suffix, valid=True)
    if mode not in _SUPPORTED_FILEMODES or "b" in mode:
      raise NotImplementedError(f"{mode!r} mode is not supported by File")
    self.writable = mode in _WRITABLE_MODES
    self.readable = mode in _READABLE_MODES
    if self.readable:
      max_bytes = 0
      max_lines = 0
    if max_bytes > 0 or max_lines > 0:
      # If rotation or rollover is wanted, it makes no sense to use
      # another mode than `a`. If for example `w` were specified,
      # then if there were multiple runs of the calling application.
      # The files from previous runs would be lost if the `w` is
      # respected, because the file would be truncated on each run.
      mode = "a"
    self.mode = mode
    self.encoding = encoding
    self.buffering = buffering
    self.max_lines = max_lines
    self.max_bytes = max_bytes
    self.file = None
    self.closed = False
    self.idx = self.index
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
  def related_files(self) -> List[str]:
    """Return names of matching files written by write method."""
    return sorted(fnmatch.filter(os.listdir(self.parent), f"{self.name}*.?"))

  @property
  def index(self) -> int:
    """Return count of files with same name."""
    return len(self.related_files) + 1

  @property
  def create(self) -> None:
    """Create an empty file if it doesn't exists."""
    if not self.file_path.exists():
      self.file_path.touch()

  def count_lines(self, file_path: Union[Path, str]) -> int:
    """Count number of lines in a file."""
    return sum(1 for _ in open(file_path, "r"))

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
    if self.writable:
      self.file.flush()

  def close(self) -> None:
    """Close file after the I/O operation."""
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
    if self.max_lines > 0:
      if self.count_lines(self.file_path) + 1 > self.max_lines:
        _rotate = True
    if _rotate:
      self.close()
      if self.file_path.exists():
        os.rename(self.file_path, f"{self.file_path}.{self.idx}")
        self.idx += 1
      else:
        raise FileNotFoundError()
      self.open()

  def write(self,
            *args: Sequence[Any],
            sep: Optional[str] = None,
            end: Optional[str] = None) -> None:
    """
    Write contents.

    Write contents to file, clearing contents of the file on first
    write and then appending on subsequent calls. This methods also
    rotates the file when needed.
    """
    if not self.writable:
      raise exceptions.PermissionDeniedError(self.name, self.mode, valid=True)
    if self.closed:
      raise exceptions.FileAlreadyClosed(file=self.name, valid=True)
    raw = list(map(lambda x: "" if x is None else str(x), args))
    sep, end = _SEP if not sep else sep, _CRLF if not end else end
    self.file.write(sep.join(raw) + end)
    self.flush()
    self.rotate()

  def read(self, files: Optional[int] = None) -> List[str]:
    """
    Read contents.

    Read contents from all the related files to a list. This method
    ensures that the data from all the files created by the write method
    is read rather than depending on the user to loop through each file.
    """
    if not self.readable:
      raise exceptions.PermissionDeniedError(self.name, self.mode, valid=True)
    if not self.closed:
      self.close()
      self.closed = True
    result = []
    if files:
      if files < 0:
        raise ValueError("File count can't be negative")
      if files > self.index:
        files = self.index + 1
    else:
      files = self.index + 1
    related_files = self.related_files + [self.name]
    for file in related_files[:files]:
      file = self.parent / Path(file)
      result += open(file, "r").readlines()
    return result
