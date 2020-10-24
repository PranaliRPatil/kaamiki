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
Kaamiki Logger

A Python based utility for logging Kaamiki events.
"""

import datetime
import logging
import os
import os.path as _os
import sys
from distutils.sysconfig import get_python_lib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Union

from kaamiki import USER, Neo, SysExcInfoType, replace_chars

__all__ = ["Logger"]

# NOTE: Most of the docstring content is referenced from the original
# logging module as we're not changing the behaviour of any of its
# implementation but rather implementing some level of scalability
# and simplicity suitable for most of the development scenarios.

DEF = "\033[0m"
BLD = "\033[1m"
RED = "\033[91m"
GRN = "\033[92m"
YLW = "\033[93m"
CYN = "\033[96m"

_colors = {
    logging.DEBUG: CYN,
    logging.INFO: GRN,
    logging.WARNING: YLW,
    logging.ERROR: RED,
    logging.CRITICAL: BLD + RED,
}


class _Formatter(logging.Formatter, metaclass=Neo):
  """
  Format logs gracefully.

  Formatter need to know how a LogRecord is constructed. They are
  responsible for converting a LogRecord to a string which can be
  interpreted. This class allows uniform formatting across various
  logging levels using the formatting string provided to it.
  If none is supplied, default template will be used.

  The Formatter can be initialized with a format which makes use
  of knowledge of the LogRecord attributes.

  This class is provided as an extension for logging records and
  traceback information in a graceful manner and the output logs
  are inspired from the `Spring Boot` framework.
  """

  def __init__(self, datefmt: str = None, fmt: str = None) -> None:
    """
    Initialize formatter.

    Initialize the formatter either with the specified format
    strings, or use default Kaamiki format as said above.
    """
    if not datefmt:
      datefmt = "%b %d, %Y %H:%M:%S"
    self.datefmt = datefmt
    self.user_fmt = True
    if not fmt:
      self.user_fmt = False
      fmt = ("%(asctime)s.%(msecs)03d %(levelname)8s %(process)07d "
             "[{:>15}] {:>30}:%(lineno)04d : %(message)s")
    self.fmt = fmt
    self.exc_fmt = "{0}: {1} {2}on line {3}"

  def formatException(self, ei: SysExcInfoType) -> str:
    """Format and return the specified exception info as a string."""
    return repr(super().formatException(ei))

  def relative_path(self, abspath: str) -> str:
    """Return relative path of the logged module."""
    sep = "kaamiki" if "kaamiki" in abspath else get_python_lib()
    return Path(abspath.partition(sep)[-1][1:].replace(os.sep, ".")).stem

  def format(self, record: logging.LogRecord) -> str:
    """Format and return the specified record as text."""
    if self.user_fmt:
      log = logging.Formatter(self.fmt, self.datefmt)
    else:
      thd = "main" if record.threadName == "MainThread" else record.threadName
      # Shorten longer module names with an ellipsis while logging.
      # This ensures length of module name stay consistent in logs.
      module = self.relative_path(record.pathname)
      if len(module) > 30:
        module = module[:27] + bool(module[27:]) * "..."
      log = logging.Formatter(self.fmt.format(thd, module), self.datefmt)
    log = log.format(record)
    if record.exc_text:
      func = record.funcName
      func = f"in {func}() " if func != "<module>" else ""
      exc_msg = self.exc_fmt.format(record.exc_info[1].__class__.__name__,
                                    record.msg,
                                    func,
                                    record.exc_info[2].tb_lineno)
      log = log.replace("\n", "").replace(str(record.exc_info[-2]), exc_msg)
      log, _, _ = log.partition("Traceback")
    return log


class _StreamHandler(logging.StreamHandler, metaclass=Neo):
  """
  StreamHandler class which add colors to the logging levels.

  StreamHandler is a handler class which writes log record to the
  output stream. The class is similar to native StreamHandler but
  with some adaptive colors and taste of Singleton design pattern.

  The colors adapt themselves with respect to the logging levels.
  Note that this class does not close the stream, as sys.stdout
  or sys.stderr may be used.
  """
  # TODO(xames3): Consider adding support to Windows systems.
  # See https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
  # for implementation for a Windows machine.

  def __init__(self) -> None:
    """Initialize stream handler."""
    super().__init__(sys.stdout)

  def render(self, level: int, record: logging.LogRecord) -> str:
    """Return color to render while displaying logs."""
    return _colors.get(level, DEF) + record.levelname

  def format(self, record: logging.LogRecord) -> str:
    """Format log level with adaptive color."""
    log = logging.StreamHandler.format(self, record)
    colored = self.render(record.levelno, record) + DEF
    return log.replace(record.levelname, colored)


class Logger(object):
  """
  Logger class for logging all active instances of Kaamiki.

  The class captures all logged Kaamiki events and logs them silently.
  Logger is packed with a convenient file handlers along with formatter
  which enables it to sequentially archive, record and clean logs.

  Logger provides flexible logging using the different arguments that
  are provided to it. If none is supplied, default set of settings are
  used. For the log format, Logger prefers the default one as it seems
  to provide all the bells and whistles right off the bat.
  However, as described above the behaviour can be changed using the
  argument(s). In this case, `datefmt` and `fmt`.

  Like any standard logger, Logger allows you to set your minimum
  logging level using `level` argument. By default, the path and
  the name of the log file is picked automatically by the Logger. The
  same can be overridden by changing the `path` and the `name` arguments
  respectively. Argument `root` is well, root logging point of the
  logger. Logger provides an option to colorize logging levels. By
  default, it is True, you can switch the behaviour using `colored`
  argument. 

  As stated above, Logger supports three primary file handlers - normal
  FileHandler, RotatingFileHandler and TimedRotatingFileHandler.
  Handlers are tools which allows logging to a set of files, which
  switches from one file to the next either when the current file
  reaches a certain size or reaches certain timed intervals, this is
  called as `Rollover` or `Rotation`.
  You can choose if the log file should rotate (rollover) or not using
  the `rotate` flag. If set to True, you can specify the type of log
  rotation i.e rotation based on log file size or rotation based on the
  certain time frame by updating the `rotate_by` argument.

  When `rotate_by` is set to "size", `Rollover` occurs whenever the
  current log file is nearly `maxBytes` in length. If `maxBytes` is
  zero, rollover never occurs. If backupCount is >= 1, the system will
  successively create new files with extensions ".1", ".2" etc.
  appended to it. For example, with a backupCount of 5 and a base file
  name of "kaamiki.log", you would get "kaamiki.log", "kaamiki.log.1",
  "kaamiki.log.2", ... through to "kaamiki.log.5". The file being
  written to is always "kaamiki.log" - when it gets filled up, it is
  closed and renamed to "kaamiki.log.1", and if files "kaamiki.log.1",
  "kaamiki.log.2" etc. exist, then they are renamed to "kaamiki.log.2",
  "kaamiki.log.3" etc. respectively.

  When `rotate_by` is set to "time" log rotation occurs at certain time
  intervals. If backupCount is > 0, when rollover is done, no more than
  backupCount files are kept - the oldest ones are deleted.

  Example:
    >>> from kaamiki.utils.logging import Logger
    >>> log = Logger().log
    >>>
    >>> log.info("This is how you use the Logger class with defaults.")
  """

  def __init__(self,
               fmt: str = None,
               datefmt: str = None,
               level: Union[int, str] = None,
               name: str = None,
               path: str = None,
               root: str = None,
               colored: bool = True,
               extra: dict = {},
               rotate: bool = True,
               rotate_by: str = "size",
               maxBytes: int = 1000000, # Rotate when logs reach 1 MB
               when: str = "h",
               interval: int = 1,
               utc: bool = False,
               atTime: datetime.datetime = None,
               backupCount: int = 5,
               encoding: str = None,
               delay: bool = False) -> None:
    """
    Initialize logger.

    Initialize the logger either with non-default values or with
    default settings. Default args are configured to work directly
    with Kaamiki, although the behaviour can be easily overridden.
    """
    self.fmt = fmt
    self.datefmt = datefmt
    self.level = logging.getLevelName(level if level else logging.DEBUG)
    self.root = root
    self.colored = colored
    self.extra = extra
    self.formatter = _Formatter(self.datefmt, self.fmt)
    self.stream = _StreamHandler() if self.colored else logging.StreamHandler()
    self.stream.setFormatter(self.formatter)
    self.rotate = rotate
    self.rotate_by = rotate_by
    self.maxBytes = maxBytes
    self.when = when
    self.interval = interval
    self.utc = utc
    self.atTime = atTime
    self.backupCount = backupCount
    self.encoding = encoding
    self.delay = delay
    try:
      self.py = _os.abspath(sys.modules["__main__"].__file__)
    except AttributeError:
      self.py = "terminal.py"
    self.name = replace_chars(name if name else Path(self.py).stem)
    self.path = path if path else _os.expanduser(f"~/.kaamiki/{USER}/logs/")
    if not _os.exists(self.path):
      os.makedirs(self.path)
    self._file = _os.join(self.path, "".join([self.name, ".log"]))
    if self.rotate:
      if self.rotate_by == "time":
        self.file = TimedRotatingFileHandler(
            self._file, self.when, self.interval, self.backupCount,
            self.encoding, self.delay, self.utc, self.atTime)
      else:
        # If rotation or rollover is wanted, it makes no sense to use
        # another mode than `a`. Hence, the `mode` argument is not
        # configurable.
        self.file = RotatingFileHandler(
            self._file, "a", self.maxBytes, self.backupCount, self.encoding,
            self.delay)
    else:
      self.file = logging.FileHandler(
          self._file, "a", self.encoding, self.delay)
    self.file.setFormatter(self.formatter)
    self.logger = logging.getLogger(self.root if self.root else None)
    self.logger.setLevel(self.level)
    self.logger.addHandler(self.file)
    self.logger.addHandler(self.stream)

  def __repr__(self) -> str:
    """Return string representation of Kaamiki's logger object."""
    return (f"<KaamikiLogger: {self.logger.name} "
            f"- [{self.level}] - {self._file}>")

  @property
  def log(self) -> logging.LoggerAdapter:
    """Return an adapter to log events."""
    return logging.LoggerAdapter(self.logger, extra=self.extra)