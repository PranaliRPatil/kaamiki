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

"""Collection of all the exceptions raised by Kaamiki framework."""

from typing import Any


class KaamikiBaseException(Exception):
    """Base exception class for all exceptions raised by Kaamiki."""

    msg = ''

    def __init__(self, valid: bool = False, **kwargs: Any) -> None:
        """Initialize exception class with exception message.

        The `valid` argument ensures that the exceptions are raised
        explicitly by the authors. This guarantees that all the known
        corner cases in the framework are handled properly or patched
        nonetheless.
        """
        if not valid:
            self.msg += self.__report_effing_bug()
        super().__init__(self.msg)
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        """Format exception message with valid arguments."""
        return self.msg.format(**vars(self))

    @staticmethod
    def __report_effing_bug() -> str:
        """Return bug reporting warning."""
        title = 'YIKES! There\'s a bug:'
        title += ''.join(('\n', '-' * len(title)))
        return (
            f'\n\n{title}\nIf you are seeing this, then there is something '
            f'wrong with Kaamiki and not your code.\nPlease report this '
            f'issue here: "https://github.com/kaamiki/kaamiki/issues/new" '
            f'so that\nwe can fix the issue at the earliest. It would be '
            f'a great help if you could provide the\nsteps, traceback '
            f'information or even a sample code for reproducing this bug '
            f'while\nsubmitting an issue.\n'
        )
