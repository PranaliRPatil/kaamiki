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
Kaamiki CLI Parser

A command line parsing utility for kaamiki. The module provides a
high-level argument parser that can handle both argument (optional and
positional) and provides helpful usage descriptions thereby exposing
the main parser.
"""

import argparse
import itertools
import os
import sys
from textwrap import TextWrapper as _wrapper
from typing import Any, List, Tuple

from kaamiki import __author__, __name__, show_version

__all__ = ["main"]

# NOTE: Do not import and use main() directly. Using it directly is
# highly discouraged. The behavior of this function is subject to
# change with time and modifications happening in the existing
# implementation, so calling it directly is probably not a good idea.

# Project URL and the copyright information should be added at the end
# of all the parser object events.
_URL = "Read complete documentation at: https://github.com/kaamiki/kaamiki"
_COPYRIGHT = f"Copyright (c) 2020 {__author__}. All rights reserved."

_USAGE = f"{__name__} <command> [options] ..."
_EPILOG = (f"For specific information about a particular command, run "
           f"\"{__name__} <command> -h\".")


class Parser(argparse.ArgumentParser):
  """
  Parse command line arguments.

  This class provides a high-level API for using instances of kaamiki
  direct from the command line. Python's builtin `ArgumentParser` is
  great but it lacks a couple of things like a simple and uniform help
  section or rather a nested description section that could help the
  users to navigate within the framework easily.

  The class also aims at using kaamiki with ease as the argument
  parsing provides the necessary function or method calls via simple
  command line inputs. The parser will then convert the command line
  strings into kaamiki instances. Most of the kaamiki objects will have
  their own set of help texts (docstrings) for understanding the
  behaviour and the implementation of a particular class or object, this
  class will provide a better visual representation of that information
  needed to parse the argument(s) to the callable instance from the
  command line.

  It enables the usage of keyword, "kaamiki" to call instances of
  kaamiki's methods.

  NOTE: The scope of this class is not to defy the behaviour of the
  builtin `ArgumentParser` but to embrace it and work as a simple
  wrapper around its feature rich implementation.
  """

  def __init__(self, *args: Any, **kwargs: Any) -> None:
    """
    Initialize parser.

    Initialize parser for converting the command line inputs into
    kaamiki objects.
    """
    self.width = round(os.get_terminal_size().columns / 1.3)
    self.program = {key: kwargs[key] for key in kwargs}
    self.commands = []
    self.options = []
    # Define program keyword, `prog` as `kaamiki` and make
    # `add_help=False` to add support for custom help message.
    super().__init__(prog=__name__, add_help=False, *args, **kwargs)

  def add_argument(self, *args: Any, **kwargs: Any) -> None:
    """
    Add arguments as inputs to called instances.

    This method defines the collection of input arguments. These
    arguments could be positional, optional or sometimes be `values`
    passed to a method.
    """
    super().add_argument(*args, **kwargs)
    argument = {key: kwargs[key] for key in kwargs}
    # Prepare list of all command arguments i.e arguments with only one
    # name and not starting with `-` and are provided as positional
    # arguments to a method (values provided to the `dest=` argument).
    if len(args) == 0 or (len(args) == 1 and
                          isinstance(args[0], str) and not
                          args[0].startswith("-")):
      argument["name"] = args[0] if len(args) > 0 else argument["dest"]
      self.commands.append(argument)
      return None
    # Prepare list of optional arguments i.e arguments with one or more
    # flags starting with `-` provided as positional argument to a
    # method.
    argument["flags"] = [arg for arg in args]
    self.options.append(argument)

  def format_usage(self) -> str:
    """
    Format helpful usage text.

    This method defines the usage block and provides information along
    with the syntax of using a particular command.

    NOTE: Not every command has `usage` information.
    """
    prefix = "Usage:\n  "
    usage = []
    # Use the below block if `usage` is provided.
    if "usage" in self.program:
      wrapper = _wrapper(self.width)
      wrapper.initial_indent = prefix
      wrapper.subsequent_indent = len(prefix) * " "
      if self.program["usage"] == "" or str.isspace(self.program["usage"]):
        return wrapper.fill("No usage information available.")
      return wrapper.fill(self.program["usage"])

    if "prog" in self.program and self.program["prog"] != "" and not \
            str.isspace(self.program["prog"]):
      prog = self.program["prog"]
    else:
      prog = os.path.basename(sys.argv[0])

    usage.append(prefix)
    for command in self.commands[:4]:
      if "metavar" in command:
        usage.append(f"{prog} {command['metavar']} [options] ...")
      else:
        usage.append(f"{prog} {command['name']} [options] ...")
      usage.append("\n  ")
    return "".join(usage[:-1])

  def format_help(self) -> Tuple[List[str], ...]:
    """
    Format command description (help) text.

    This method returns modular (tuple of strings) snippets of help
    texts that are used for displaying the help.
    """
    description, commands, options, epilog = [], [], [], []
    args_len = desc_len = 0
    # Wrap epilog and the command description into a paragraph if the
    # string exceeds a set width. This ensures consistency in the help
    # text's alignment.
    epilog_wrapper = _wrapper(self.width, replace_whitespace=False)
    desc_wrapper = _wrapper(self.width, replace_whitespace=False)
    desc_wrapper.subsequent_indent = 2 * " "
    # Add description if provided.
    if "description" in self.program and \
            self.program["description"] != "" and not \
            str.isspace(self.program["description"]):
      description.append("\nDescription:\n  ")
      description.extend(desc_wrapper.wrap(self.program["description"]))
      description.append("\n")

    for command in self.commands:
      if "metavar" in command:
        command["left"] = command["metavar"]
      else:
        command["left"] = command["name"]

    for option in self.options:
      if "action" in option and (option["action"] == "store_true" or
                                 option["action"] == "store_false"):
        option["left"] = str.join(", ", option["flags"])
      else:
        flags = []
        for item in option["flags"]:
          if "metavar" in option:
            flags.append(f"{item} <{option['metavar']}>")
          elif "dest" in option:
            flags.append(f"{item} {option['dest'].upper()}")
          else:
            flags.append(item)
        option["left"] = str.join(", ", flags)

    for argument in self.commands + self.options:
      if "help" in argument and argument["help"] != "" and not \
              str.isspace(argument["help"]) and \
              "default" in argument and argument["default"] != \
              argparse.SUPPRESS:
        if isinstance(argument["default"], str):
          argument["right"] = argument["help"] + " " + \
              f"(Default: {argument['default']})"
        else:
          argument["right"] = argument["help"] + " " + \
              f"(Default: {argument['default']})"
      elif "help" in argument and argument["help"] != "" and not \
              str.isspace(argument["help"]):
        argument["right"] = argument["help"]
      elif "default" in argument and argument["default"] != argparse.SUPPRESS:
        if isinstance(argument["default"], str):
          argument["right"] = f"Default: '{argument['default']}'"
        else:
          argument["right"] = f"Default: {str(argument['default'])}"
      else:
        argument["right"] = "No description available."
      args_len = max(args_len, len(argument["left"]))
      desc_len = max(desc_len, len(argument["right"]))

    # Calculate maximum width required for displaying the args and
    # their respective descriptions. We are limiting the width of args
    # description to maximum of self.width / 2. We use max() to prevent
    # negative values.
    argswidth = args_len
    descwidth = max(0, self.width - argswidth - 4)
    if (argswidth > int(self.width / 2) - 4):
      argswidth = max(0, int(self.width / 2) - 4)
      descwidth = int(self.width / 2)

    # Define template with two leading spaces and two trailing spaces
    # (spaces between args and description).
    template = "  %-" + str(argswidth) + "s  %s"

    # Wrap text for args and description parts by splitting the text
    # into separate lines.
    args_wrapper = _wrapper(argswidth)
    desc_wrapper = _wrapper(descwidth)
    for argument in self.commands + self.options:
      argument["left"] = args_wrapper.wrap(argument["left"])
      argument["right"] = desc_wrapper.wrap(argument["right"])

    # Add command arguments.
    if len(self.commands) > 0:
      commands.append("\nCommands:\n")
      for command in self.commands:
        for idx in range(max(len(command["left"]), len(command["right"]))):
          if idx < len(command["left"]):
            left = command["left"][idx]
          else:
            left = ""
          if idx < len(command["right"]):
            right = command["right"][idx]
          else:
            right = ""
          commands.append(template % (left, right))
          commands.append("\n")

    # Add option arguments.
    if len(self.options) > 0:
      options.append("\nOptions:\n")
      for option in self.options:
        for idx in range(max(len(option["left"]), len(option["right"]))):
          if idx < len(option["left"]):
            left = option["left"][idx]
          else:
            left = ""
          if idx < len(option["right"]):
            right = option["right"][idx]
          else:
            right = ""
          options.append(template % (left, right))
          options.append("\n")

    # Add epilog if provided.
    if "epilog" in self.program and self.program["epilog"] != "" and not \
            str.isspace(self.program["epilog"]):
      epilog.append("\n")
      epilog.extend(epilog_wrapper.wrap(self.program["epilog"]))
      epilog.append(f"\n{_URL}\n\n{_COPYRIGHT}\n")

    return description, commands, options, epilog

  def print_help(self) -> None:
    """Print help to sys.stdout."""
    sys.stdout.write(f"\n{self.format_usage()}\n")
    sys.stdout.write("".join(list(itertools.chain(*self.format_help()))))
    sys.stdout.flush()

  def error(self) -> None:
    """Print hint to stderr and exit."""
    sys.stderr.write(f"\n{self.format_usage()}\n")
    sys.stderr.write("".join(list(itertools.chain(*self.format_help()))))
    sys.exit(1)


def _create_parser() -> Parser:
  """
  Return parser to parse the command line input.

  The function is powered by `Parser` class which acts like an entry
  point for kaamiki when used on command line. It enables the method
  or function calls from kaamiki suite using simple commands.
  """
  # NOTE(xames3): Consider adding support for subparsers in future.
  parser = Parser(usage=_USAGE, epilog=_EPILOG, conflict_handler="resolve")
  parser.add_argument("-h", "--help", action="store_true",
                      help="Show this help message.",
                      default=argparse.SUPPRESS)
  parser.add_argument("-V", "--version", action="store_true",
                      help="Show installed kaamiki version.",
                      default=argparse.SUPPRESS)
  return parser


def main() -> None:
  """Primary kaamiki entry point."""
  parser = _create_parser()
  args = parser.parse_args()

  if hasattr(args, "function"):
    args.function(args)
  elif hasattr(args, "version"):
    show_version()
  else:
    parser.print_help()
