# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the pydidas excepthook for the GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["gui_excepthook"]

import os
import time
import traceback
from io import StringIO

from ..core.utils import get_logging_dir
from .dialogues import ErrorMessageBox


def gui_excepthook(exc_type, exception, trace):
    """
    Catch global exceptions.

    This global function is used to replace the generic sys.excepthook
    to handle exceptions. It will open a popup window with the exception
    text.

    Parameters
    ----------
    exc_type : type
        The exception type
    exception : Exception
        The exception itself.
    trace : traceback object
        The trace of where the exception occured.
    """
    _traceback_info = StringIO()
    traceback.print_tb(trace, None, _traceback_info)
    _traceback_info.seek(0)
    _trace = _traceback_info.read()
    _logfile = os.path.join(get_logging_dir(), "pydidas_exception.log")

    _time = time.strftime("%Y-%m-%d %H:%M:%S")
    _sep = "\n" + "-" * 20 + "\n"
    _msg = "-" * 20 + "\n" + _sep.join([_time, f"{exc_type}: {exception}", _trace])
    with open(_logfile, "a+") as _file:
        _file.write("\n\n" + _msg)

    _ = ErrorMessageBox(text=_msg).exec_()
