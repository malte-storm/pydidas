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
Module with the BaseParamIoWidgetMixIn base class which all widgets for editing
Parameters should inherit from (in addition to their respective QWidget).
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseParamIoWidgetMixIn"]


import html
import numbers
import pathlib

from numpy import nan
from qtpy import QtCore, QtGui

from ...core import Hdf5key, Parameter, UserConfigError
from ...core.constants import (
    PARAM_INPUT_EDIT_WIDTH,
    PARAM_INPUT_WIDGET_HEIGHT,
    QT_REG_EXP_FLOAT_VALIDATOR,
    QT_REG_EXP_INT_VALIDATOR,
)


LOCAL_SETTINGS = QtCore.QLocale(QtCore.QLocale.C)
LOCAL_SETTINGS.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)

FLOAT_VALIDATOR = QtGui.QDoubleValidator()
FLOAT_VALIDATOR.setNotation(QtGui.QDoubleValidator.ScientificNotation)
FLOAT_VALIDATOR.setLocale(LOCAL_SETTINGS)


class BaseParamIoWidgetMixIn:
    """
    Base mixin class of widgets for I/O during Parameter editing.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    width: int, optional
        The width of the IO widget. The default is the PARAM_INPUT_EDIT_WIDTH
        specified in pydidas.core.constants.gui_constants.
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param: Parameter, **kwargs: dict):
        self.setFixedWidth(kwargs.get("width", PARAM_INPUT_EDIT_WIDTH))
        self.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)
        self._ptype = param.dtype
        self._old_value = None
        self.setToolTip(f"<qt>{html.escape(param.tooltip)}</qt>")

    def set_validator(self, param: Parameter):
        """
        Set the widget's validator based on the Parameter's configuration.

        Parameters
        ----------
        param : pydidas.core.Parameter
            The associated Parameter.
        """
        if param.dtype == numbers.Integral:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_INT_VALIDATOR)
            else:
                self.setValidator(QtGui.QIntValidator())
        elif param.dtype == numbers.Real:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_FLOAT_VALIDATOR)
            else:
                self.setValidator(FLOAT_VALIDATOR)

    def get_value_from_text(self, text: str) -> object:
        """
        Get a value from the text entry to update the Parameter value.

        Parameters
        ----------
        text : str
            The input string from the input field.

        Returns
        -------
        type
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        # need to process True and False explicitly because bool is a subtype
        # of int but the strings 'True' and 'False' cannot be converted to int
        if text.upper() == "TRUE":
            return True
        if text.upper() == "FALSE":
            return False
        if text.upper() == "NAN":
            return nan
        if text.upper() == "NONE":
            return None
        try:
            if self._ptype == numbers.Integral:
                return int(text)
            if self._ptype == numbers.Real:
                return float(text)
            if self._ptype == pathlib.Path:
                return pathlib.Path(text)
            if self._ptype == Hdf5key:
                return Hdf5key(text)
        except ValueError as _error:
            _msg = str(_error)
            _msg = _msg[0].upper() + _msg[1:]
            raise UserConfigError(f'ValueError! {_msg} Input text was "{text}"')
        return text

    def emit_signal(self):
        """
        Emit a signal.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own emit_signal method,
            this exception will be raised.
        """
        raise NotImplementedError

    def get_value(self):
        """
        Get the value from the input field.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own get_value method,
            this exception will be raised.
        """
        raise NotImplementedError

    def set_value(self, value):
        """
        Set the input field's value.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own set_value method,
            this exception will be raised.
        """
        raise NotImplementedError