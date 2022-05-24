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
Module with the critical_warning function for creating a warning with a
simplified syntax.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["critical_warning"]

from qtpy import QtWidgets

from ..utilities import get_pyqt_icon_from_str_reference


def critical_warning(title, text):
    """
    Create a QMessageBox with a critical warning and show it.

    Parameters
    ----------
    title : str
        The warning title.
    text : str
        The warning message text.
    """

    _box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, title, text)
    _box.setWindowIcon(get_pyqt_icon_from_str_reference("qt-std::11"))
    _box.exec_()
