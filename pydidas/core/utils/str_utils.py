# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The str_utils module includes convenience functions for string formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "get_fixed_length_str",
    "get_time_string",
    "get_short_time_string",
    "timed_print",
    "get_warning",
    "convert_unicode_to_ascii",
    "convert_special_chars_to_unicode",
    "get_range_as_formatted_string",
    "update_separators",
    "format_input_to_multiline_str",
    "get_random_string",
    "get_simplified_array_representation",
]


import os
import random
import re
import string as _string_
import sys
import time
from collections.abc import Iterable
from numbers import Integral, Real
from typing import Union

import numpy as np

from ..constants import GREEK_ASCII_TO_UNI, GREEK_UNI_TO_ASCII


def get_fixed_length_str(
    obj: str,
    length: int,
    fill_back: bool = True,
    fill_char: str = ".",
    formatter: str = "{:.3f}",
    final_space: bool = True,
) -> str:
    """
    Format an input object to a string of defined length.

    Numerical objects (integer, float) will be converted to a string with
    the formatter defined in the call, input strings will be processed
    as they are.
    If the string is shorter than the required length, it will be filled with
    chars defined in the call, either in the front or back.

    Parameters
    ----------
    obj : str
        The input string to be formatted.
    length : int
        The length of the output string.
    fill_back: bool, optional
        Keyword to toggle filling the front or end.
        The default is True (filling the end of the string).
    fill_char : char, optional
        The character used for filling the string. Note that if a string is
        padded, a space is always preserved between the padding and the input.
        The default is '.'.
    formatter : str, optional
        The formatter to convert numbers to strings. The default is "{:.3f}".
    final_space: bool, optional
        A keyword to add a final space to the return string. This will be
        within the length defined in the input parameter. The default is True.

    Returns
    -------
    str
        The formatted string.
    """
    if len(fill_char) != 1:
        raise TypeError("fill_char must be exactly one character.")
    if issubclass(type(obj), Real):
        obj = formatter.format(obj)
    if not isinstance(obj, str):
        obj = repr(obj)
    if len(obj) + final_space >= length:
        return obj[: length - final_space] + " " * final_space
    _n = length - len(obj) - 1 - final_space
    return (
        _n * fill_char * (not fill_back)
        + " " * (not fill_back)
        + obj
        + " " * (fill_back)
        + _n * fill_char * (fill_back)
        + " " * final_space
    )


def get_time_string(epoch: Union[float, None] = None, human_output: bool = True) -> str:
    """
    Return a formatted time string.

    This function creates a string output of a time in the format
    (YYYY/MM/DD HH:MM:ss.sss). If no epoch-time is specified, the current
    system time will be used.

    Parameters
    ----------
    epoch : Union[float, None]
        Keyword to process an epoch input. If None, the current
        system time will be used. The default is None.

    human_output : bool, optional
        Keyword to control special  separation characters. If True, the
        output will be human-readable friendly (with special sep. chars).
        If False, only a "_" will be included between the date and time.
        The default is True.

    Returns
    -------
    str :
        The formatted date and time string.
        If human-readible: (YYYY/MM/DD HH:MM:ss.sss)
        Else: YYYYMMDD_HHMMss
    """
    if epoch is None:
        epoch = time.time()
    _time = time.localtime(epoch)
    _sec = _time[5] + epoch - np.floor(epoch)
    _str = (
        f"{_time[0]:04d}/{_time[1]:02d}/{_time[2]:02d} "
        f"{_time[3]:02d}:{_time[4]:02d}:{_sec:06.3f}"
    )
    if not human_output:
        return _str.replace("/", "").replace(" ", "_")
    return _str


def get_short_time_string(epoch: Union[float, None] = None) -> str:
    """
    Return a short time string in the format (DD/MM HH:MM:ss).

    Parameters
    ----------
    epoch : Union[float, None]
        Keyword to process an epoch input. If None, the current
        system time will be used. The default is None.

    Returns
    -------
    str :
        Formatted date and time string (DD/MM HH:MM:ss)
    """
    return get_time_string(epoch)[5:-4]


def timed_print(string: str, new_lines: int = 0, verbose: bool = True):
    """
    Print a string with a time prefix.

    This function prints a time prefix in the format YYYY/MM/DD HH:MM:ss.sss
    and the input string. If new_lines > 0, a number of new lines will be
    printed before the output is returned.

    Parameters
    ----------
    string : str
        The input string to be printed.

    new_lines : int, optional
        The number of preceding empty lines. The default is 0.

    verbose : bool, optinoal
        Keyword to "mute" the output, i.e. prevent any text to be printed.
        If True, the output will be printed, if False, this function will
        do nothing. The default is True.
    """
    if verbose:
        print("\n" * new_lines + f"{get_time_string()}: {string}")


def get_warning(
    string: str,
    severe: bool = False,
    new_lines: int = 0,
    print_warning: bool = True,
    return_warning: bool = False,
) -> Union[str, None]:
    """
    Generate a warning message (formatted string in a "box" of dashes).

    This function will create a warning string and add a box of dashes around
    it. The output to sys.stdout can be controlled with "print_warning" and
    the formatted string can be returned with the "return_warning" keyword.

    Parameters
    ----------
    string : Union[str, list, tuple]
        The input string to be formatted. A multi-line string can be passed
        as a list or tuple of strings.
    severe : bool, optional
        Keyword to add an additional frame of double dashes. The default is
        False.
    new_lines : int, optional
        The number of preceding empty lines. The default is 0.
    print_warning : bool, optional
        Keyword to print the warning to sys.stdout. The default is True.
    return_warning: bool, optional
        Keyword to get the formatted string as return argument. The default
        is False.

    Returns
    -------
    Union[None, str]
        If "return_warning" is True, the function returns the formatted string.
        Else, it will return None.
    """
    if isinstance(string, str):
        _max = len(string)
        string = [string]
    elif isinstance(string, (list, tuple)):
        _max = np.amax(np.r_[[len(_s) for _s in string]])
    _length = 60 if _max <= 54 else 80
    _s = "\n" * new_lines + severe * ("=" * _length + "\n") + "-" * _length + "\n"
    for item in string:
        _ll = len(item)
        if _ll == 0:
            _s += "-" * _length + "\n"
        elif _ll <= 77:
            _filler = "-" * (_length - _ll - 3)
            _s += f"- {item} {_filler}\n"
        else:
            _s += f"- {item[:73]}[...]\n"
    _s += "-" * _length + severe * ("\n" + "=" * _length)
    if print_warning:
        print(_s)
    if return_warning:
        return _s
    return None


def convert_special_chars_to_unicode(obj: Union[str, list]) -> Union[str, list]:
    """
    Convert a selection of special characters to unicode.

    This method will convert Greek letters, Angstrom and ^-1 to unicode.

    Parameters
    ----------
    obj : Union[str, list]
        The input string or list of strings.

    Returns
    -------
    Union[str, list]
        The updated string or list.
    """
    if isinstance(obj, list):
        new_obj = [convert_special_chars_to_unicode(entry) for entry in obj]
        return new_obj
    if isinstance(obj, str):
        _parts = obj.split()
        for _index, _part in enumerate(_parts):
            if _part in GREEK_ASCII_TO_UNI.keys():
                _parts[_index] = GREEK_ASCII_TO_UNI[_part]
        obj = " ".join(_parts)
        # insert Angstrom sign (in context of ^-1):
        obj = obj.replace("A^-1", "\u212b\u207b\u00B9")
        obj = obj.replace("^-1", "\u207b\u00B9")
        return obj
    raise TypeError(f"Cannot process objects of type {type(obj)}")


def convert_unicode_to_ascii(obj: Union[str, list]) -> Union[str, list]:
    """
    Convert a selection of special unicode characters to ASCII.

    This method will convert Greek letters, Angstrom and ^-1 to ASCII
    representations.

    Parameters
    ----------
    obj : Union[str, list]
        The input string or list of strings.

    Returns
    -------
    Union[str, list]
        The updated string or list.
    """
    if isinstance(obj, list):
        new_obj = [convert_unicode_to_ascii(entry) for entry in obj]
        return new_obj
    if isinstance(obj, str):
        _parts = obj.split()
        for _index, _part in enumerate(_parts):
            if _part in GREEK_UNI_TO_ASCII:
                _parts[_index] = GREEK_UNI_TO_ASCII[_part]
        obj = " ".join(_parts)
        obj = obj.replace("\u212b", "A")
        obj = obj.replace("\u207b\u00B9", "^-1")
        return obj
    raise TypeError(f"Cannot process objects of type {type(obj)}")


def get_range_as_formatted_string(obj: Union[np.ndarray, Iterable[float, ...]]) -> str:
    """
    Get a formatted string representation of an iterable range.

    Parameters
    ----------
    _range : Union[np.ndarray, Iterable[float, ...]]
        The input range.

    Returns
    -------
    str :
        The formatted string representation
    """
    if isinstance(obj, str):
        return obj
    try:
        _min, _max = obj[0], obj[-1]
        _str_items = []
        for _item in [_min, _max]:
            if isinstance(_item, Integral):
                _item = f"{_item:d}"
            elif isinstance(_item, Real):
                _item = f"{_item:.6f}"
            else:
                _item = str(_item)
            _str_items.append(_item)
        return _str_items[0] + " ... " + _str_items[1]
    except TypeError:
        return "unknown range"


def get_simplified_array_representation(
    obj: np.ndarray, max_items: int = 6, leading_indent: int = 4
) -> str:
    """
    Get a simplified representation of an array.

    Parameters
    ----------
    obj : np.ndarray
        The input array.
    max_items : int, optional
        The maximum number of data entries. The default is 6.
    leading_indent : int, optional
        The leading indent of each line.

    Returns
    -------
    repr : str
        The simplified string representation of the array values.
    """
    _repr = ""
    if obj.ndim > 1:
        _repr = (
            "["
            + get_simplified_array_representation(obj[0]).strip()
            + (",\n...,\n" if obj.shape[0] > 2 else ",\n")
            + get_simplified_array_representation(obj[-1])
            + "]"
        )
    elif obj.ndim == 1:
        if obj.size <= max_items:
            _items = [np.round(o, 4) for o in obj]
        else:
            _items = [np.round(o, 4) for o in obj[np.r_[0, 1, -2, -1]]]
            _items.insert(2, "...")
        _repr += "[" + ", ".join(str(item) for item in _items) + "]"
    _indent = " " * leading_indent
    _repr = "\n".join(_indent + _item.strip() for _item in _repr.split("\n"))
    return _repr


def update_separators(path: str) -> str:
    """
    Check the separators and update to os.sep if required.

    Parameters
    ----------
    path : str
        The file path to be checked

    Returns
    -------
    str
        The path with separators updated to os.sep standard.
    """
    if sys.platform in ["win32", "win64"]:
        return path.replace("/", os.sep)
    return path.replace("\\", os.sep)


def format_input_to_multiline_str(
    input_str: str,
    max_line_length: int = 60,
    pad_to_max_length: bool = False,
    keep_linebreaks: bool = True,
) -> str:
    """
    Format an input string by changing linebreaks to limit the maximum line length.

    This function will split the input string and join fragments as long as
    the length of the joint fragment is less or equal to the defined maximum
    length. Longer words will be kept as single entries.
    All fragments will be joined by linebreaks to return a single string.

    Parameters
    ----------
    input_str : str
        The input string
    max_line_length : int, optional
        The maximum length of each line in characters. The default is 60.
    pad_to_max_length : bool, optional
        Flag to toggle padding of each line to the maximum line length.
        If False, no padding is added. The default is False.
    keep_linebreaks : bool, optional
        Flag to keep linebreaks in the final formatting. The default is True.

    Returns
    -------
    str
        The input string, formatted with linebreaks at the required
        positions.
    """
    if keep_linebreaks:
        _result_lines = []
        _tmp_lines = input_str.split("\n")
        for _curr_line in _tmp_lines:
            _result_lines.extend(_get_unformatted_lines(_curr_line, max_line_length))
    if not keep_linebreaks:
        _result_lines = _get_unformatted_lines(input_str, max_line_length)
    if pad_to_max_length:
        for _index, _item in enumerate(_result_lines):
            _delta = max(0, max_line_length - len(_item))
            _delta_front = _delta // 2
            _delta_back = _delta // 2 + _delta % 2
            _result_lines[_index] = " " * _delta_front + _item + " " * _delta_back
    return "\n".join(_result_lines)


def _get_unformatted_lines(input_str: str, max_line_length: int = 60) -> list:
    """
    Get the input string in lines of a defined maximum length, ignoring linebreaks.

    Parameters
    ----------
    input_str : str
        The input string
    max_line_length : int, optional
        The maximum length of each line in characters. The default is 60.

    Returns
    -------
    result_lines : list
        The list with the individual lines.
    """
    _words = [s for s in re.split(" |\n", input_str) if len(s) > 0]
    _result_lines = []
    _current_str = _words.pop(0) if len(_words) > 0 else ""
    while len(_words) > 0:
        _newword = _words.pop(0)
        if len(_current_str + _newword) + 1 > max_line_length:
            _result_lines.append(_current_str)
            _current_str = _newword
        else:
            _current_str = f"{_current_str} {_newword}"
    _result_lines.append(_current_str)
    return _result_lines


def get_random_string(length: int, use_digits: bool = False) -> str:
    """
    Get a random string of a specific length.

    Parameters
    ----------
    length : int
        The length of the output string.
    use_digits : bool, optional
        Flag to include digits in the random string. The default is False.

    Returns
    -------
    str
        The random string.
    """
    _chars = _string_.ascii_letters + (_string_.digits if use_digits else "")
    return "".join(random.choice(_chars) for _ in range(length))
