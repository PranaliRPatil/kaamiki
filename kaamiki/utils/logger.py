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
#     PranaliRPatil <43814215+PranaliRPatil@users.noreply.github.com>

"""
Kaamiki Logger

A Python based utility for logging Kaamiki events.
"""

import datetime
import logging
import os
import sys
from distutils.sysconfig import get_python_lib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from types import TracebackType as _type
from typing import Any, Dict, Optional, Tuple, Union

from kaamiki import BASE_DIR, SESSION_USER, Neo, __name__, replace_chars
from kaamiki.utils.exceptions import InvalidArgumentError

__all__ = ["Logger"]

# NOTE: Most of the docstring content is referenced from the original
# logging module as we are not changing the behaviour of any of its
# implementation but rather adding some level of scalability, simplicity
# and flexibility that is required in most of the development scenarios.

_LOGS_DIR = "logs"

# NOTE: All log events are recorded in `_DEFAULT_LOG_PATH` by default,
# if not being overridden while instantiating. Kaamiki doesn't record
# error logs seperately!
_DEFAULT_LOG_PATH = BASE_DIR / SESSION_USER / _LOGS_DIR

# Logging formats for kaamiki. These are formats for date, exception
# logging message and the log record. Only `_DEFAULT_EXC_FMT` is not an
# available option for changing.
_DEFAULT_DATE_FMT = "%b %d, %Y %H:%M:%S"
_DEFAULT_LOG_FMT = ("%(asctime)s.%(msecs)03d %(levelname)8s "
                    "%(process)07d [{:>15}] {:>30}:%(lineno)04d : %(message)s")
_DEFAULT_EXC_FMT = "{0}: {1} {2}on line {3}."

# Character limit for displaying the module name which is logging the
# record. This value is useful only in case the logger in use uses the
# default kaamiki logging format.
_DEFAULT_MODULE_NAME_LIMIT = 30

_LOG_LEVELS = [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARNING",
    "WARN",
    "INFO",
    "DEBUG",
    "NOTSET",
]

RESET = "\u001b[39m"
GRAY = "\u001b[38;5;244m"
RED = "\u001b[38;5;196m"
GREEN = "\u001b[38;5;46m"
YELLOW = "\u001b[38;5;11m"
BLUE = "\u001b[38;5;39m"
CYAN = "\u001b[38;5;14m"
ORANGE = "\u001b[38;5;208m"

_colors = {
    logging.CRITICAL: RED,
    logging.ERROR: ORANGE,
    logging.WARNING: YELLOW,
    logging.INFO: GREEN,
    logging.DEBUG: GRAY,
    logging.NOTSET: CYAN,
}


class _Formatter(logging.Formatter, metaclass=Neo):
  """
  Format logs gracefully.

  Formatter need to know how a `LogRecord` is constructed. They are
  responsible for converting a `LogRecord` to a string which can be
  interpreted. This class allows uniform formatting across various
  logging levels using the formatting string provided to it.
  If none is supplied, default template will be used.

  The _Formatter can be initialized with a format which makes use
  of knowledge of the `LogRecord` attributes.

  This class is provided as an extension for logging records and
  traceback information in a graceful manner and the output logs
  are inspired from the `Spring Boot` framework.
  """

  def __init__(self,
               date_fmt: Optional[str] = None,
               fmt: Optional[str] = None,
               traceback: bool = False) -> None:
    """
    Initialize formatter.

    Initialize the formatter either with the specified format
    strings, or use default kaamiki format as said above.
    """
    if not date_fmt:
      date_fmt = _DEFAULT_DATE_FMT
    self.date_fmt = date_fmt
    self.user_fmt = True
    if not fmt:
      self.user_fmt = False
      fmt = _DEFAULT_LOG_FMT
    self.fmt = fmt
    self.exc_fmt = _DEFAULT_EXC_FMT
    self.traceback = traceback

  def formatException(self, ei: Tuple[type, BaseException, _type]) -> str:
    """Format and return the specified exception info as a string."""
    return repr(super().formatException(ei))

  def relative_path(self, abspath: str) -> str:
    """Return relative path of the logged module."""
    sep = __name__ if __name__ in abspath else get_python_lib()
    return Path(abspath.partition(sep)[-1][1:].replace(os.sep, ".")).stem

  def format(self, record: logging.LogRecord) -> str:
    """Format and return the specified record as text."""
    if self.user_fmt:
      log = logging.Formatter(self.fmt, self.date_fmt)
    else:
      thd = "main" if record.threadName == "MainThread" else record.threadName
      # Shorten longer module names with an ellipsis while logging.
      # This ensures length of module name stay consistent in logs.
      module = self.relative_path(record.pathname)
      if len(module) > _DEFAULT_MODULE_NAME_LIMIT:
        module = (module[:_DEFAULT_MODULE_NAME_LIMIT - 3] +
                  bool(module[_DEFAULT_MODULE_NAME_LIMIT - 3:]) * "...")
      log = logging.Formatter(self.fmt.format(thd, module), self.date_fmt)
    log = log.format(record)
    if not self.traceback:
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
  Add colors to the logging levels.

  _StreamHandler is a handler class which writes log record to the
  output stream. The class is similar to native StreamHandler but with
  some adaptive colors and taste of Singleton design pattern across
  major platforms.

  The colors adapt themselves with respect to the logging levels. Note
  that this class does not close the stream, as sys.stdout or sys.stderr
  may be used.
  """

  def __init__(self) -> None:
    """Initialize stream handler."""
    # See https://stackoverflow.com/a/64222858/14316408 for rendering
    # colors on a Windows terminal with EASE!
    if os.name == "nt":
      os.system("color")
    super().__init__(sys.stdout)

  def render(self, level: int, record: logging.LogRecord) -> str:
    """Return color to render while displaying logs."""
    return _colors.get(level, RESET) + record.levelname

  def format(self, record: logging.LogRecord) -> str:
    """Format log level with adaptive color."""
    log = logging.StreamHandler.format(self, record)
    colored = self.render(record.levelno, record) + RESET
    return log.replace(record.levelname, colored)


class Logger(logging.LoggerAdapter):
  """
  Logger class for logging all active instances of kaamiki.

  The class captures all logged kaamiki events and logs them silently.
  Logger is packed with a convenient file handlers along with formatter
  which enables it to sequentially archive, record and clean logs.

  Logger provides flexible logging using the different arguments that
  are provided to it. If none is supplied, default set of settings are
  used. For the log format, Logger prefers the default one as it seems
  to provide all the bells and whistles right off the bat.
  However, as described above the behaviour can be changed using the
  argument(s). In this case, `date_fmt` and `fmt`.

  Like any standard logger, Logger allows you to set your minimum
  logging level using `level` argument. By default, the path and
  the name of the log file is picked automatically by the Logger. The
  same can be overridden by changing the `path` and the `name` arguments
  respectively. Argument `root` is well, root logging point of the
  logger. Logger provides an option to colorize logging levels. By
  default, it is True, you can switch the behaviour using `colored`
  argument. 

  As stated above, Logger supports three primary file handlers - normal
  `FileHandler`, `RotatingFileHandler` and `TimedRotatingFileHandler`.
  Handlers are tools which allows logging to a set of files, which
  switches from one file to the next either when the current file
  reaches a certain size or reaches certain timed intervals, this is
  called as `Rollover` or `Rotation`.
  You can choose if the log file should rotate (rollover) or not using
  the `rotate` flag. If set to True, you can specify the type of log
  rotation i.e rotation based on log file size or rotation based on the
  certain time frame by updating the `rotate_by` argument.

  When `rotate_by` is set to "size", `Rollover` occurs whenever the
  current log file is nearly `max_bytes` in length. If `max_bytes` is
  zero, rollover never occurs. If `backups` is >= 1, the system will
  successively create new files with extensions ".1", ".2" etc.
  appended to it. For example, with a backups of 5 and a base file
  name of "kaamiki.log", you would get "kaamiki.log", "kaamiki.log.1",
  "kaamiki.log.2", ... through to "kaamiki.log.5". The file being
  written to is always "kaamiki.log" - when it gets filled up, it is
  closed and renamed to "kaamiki.log.1", and if files "kaamiki.log.1",
  "kaamiki.log.2" etc. exist, then they are renamed to "kaamiki.log.2",
  "kaamiki.log.3" etc. respectively.

  When `rotate_by` is set to "time" log rotation occurs at certain time
  intervals. If `backups` is > 0, when rollover is done, no more than
  backups files are kept - the oldest ones are deleted.

  Example:
    >>> from kaamiki.utils.logger import Logger
    >>> logger = Logger()
    >>>
    >>> logger.info("This is how you use the Logger class")
  """

  suffix = ".log"

  def __init__(self,
               fmt: Optional[str] = None,
               date_fmt: Optional[str] = None,
               level: Optional[Union[int, str]] = None,
               name: Optional[str] = None,
               path: Optional[Union[Path, str]] = None,
               root: str = None,
               colored: Optional[bool] = True,
               traceback: bool = False,
               extra: Optional[Dict[str, Any]] = None,
               rotate: Optional[bool] = True,
               rotate_by: str = "size",
               max_bytes: int = 0,
               when: str = "h",
               interval: int = 1,
               utc: bool = False,
               at_time: Optional[datetime.datetime] = None,
               backups: int = 0,
               encoding: Optional[str] = None,
               delay: bool = False,
               to_file: Optional[bool] = True) -> None:
    """
    Initialize logger.

    Initialize the logger either with default or non-default settings.
    Default args are configured to work directly with kaamiki, although
    the behaviour can be easily overridden.
    """
    self.fmt = fmt
    self.date_fmt = date_fmt
    if not isinstance(level, (int, str)) and level is not None:
      raise InvalidArgumentError(arg=level, valid=True)
    if isinstance(level, str) and level not in _LOG_LEVELS:
      raise ValueError(
          f"{level!r} is not a valid logging level. "
          f"Choose correct logging level from these available options: "
          f"{', '.join(_LOG_LEVELS[:-2] + [' and '.join(_LOG_LEVELS[-2:])])}")
    self.level = logging.getLevelName(level if level else logging.DEBUG)
    self.root = root
    self.colored = colored
    self.traceback = traceback
    self.extra = extra if extra else {}
    self.rotate = rotate
    self.rotate_by = rotate_by
    self.max_bytes = max_bytes
    self.when = when
    self.interval = interval
    self.utc = utc
    self.at_time = at_time
    self.backups = backups
    self.encoding = encoding
    self.delay = delay
    self.to_file = to_file
    self.formatter = _Formatter(self.date_fmt, self.fmt, self.traceback)
    self.stream = _StreamHandler() if self.colored else logging.StreamHandler()
    self.stream.setFormatter(self.formatter)
    self.logger = logging.getLogger(self.root if self.root else None)
    self.logger.setLevel(self.level)
    try:
      self.py = os.path.abspath(sys.modules["__main__"].__file__)
    except AttributeError:
      self.py = "console.py"
    self._name = replace_chars(name if name else Path(self.py).stem)
    self.path = path if path else _DEFAULT_LOG_PATH
    if not Path(self.path).exists():
      os.makedirs(self.path)
    if self.to_file:
      self.file_path = Path(self.path) / (self._name + self.suffix)
      if self.rotate:
        if self.rotate_by not in ("size", "time"):
          raise InvalidArgumentError(arg=self.rotate_by, valid=True)
        if self.rotate_by == "time":
          self.file = TimedRotatingFileHandler(
              self.file_path, self.when, self.interval, self.backups,
              self.encoding, self.delay, self.utc, self.at_time)
        else:
          # If rotation or rollover is wanted, it makes no sense to use
          # another mode than `a`. Hence, it is not configurable.
          self.file = RotatingFileHandler(
              self.file_path, "a", self.max_bytes, self.backups, self.encoding,
              self.delay)
      else:
        self.file = logging.FileHandler(
            self.file_path, "a", self.encoding, self.delay)
      self.file.setFormatter(self.formatter)
      self.logger.addHandler(self.file)
    self.logger.addHandler(self.stream)

  def __repr__(self) -> str:
    """Return the canonical string representation of kaamiki logger."""
    return f"{self.__class__.__name__}(root={self.root!r})"

  def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log message with `CRITICAL` logging level."""
    for line in str(msg).splitlines():
      self.logger.critical(line, *args, **kwargs, stacklevel=2)

  def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log message with `ERROR` logging level."""
    for line in str(msg).splitlines():
      self.logger.error(line, *args, **kwargs, stacklevel=2)

  def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log message with `WARNING` logging level."""
    for line in str(msg).splitlines():
      self.logger.warning(line, *args, **kwargs, stacklevel=2)

  def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log message with `INFO` logging level."""
    for line in str(msg).splitlines():
      self.logger.info(line, *args, **kwargs, stacklevel=2)

  def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log message with `DEBUG` logging level."""
    for line in str(msg).splitlines():
      self.logger.debug(line, *args, **kwargs, stacklevel=2)

  def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
    """Log exception with traceback."""
    self.logger.error(msg, *args, **kwargs, exc_info=True, stacklevel=2)

  fatal = critical
  warn = warning