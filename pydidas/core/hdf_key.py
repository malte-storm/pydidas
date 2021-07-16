# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
The parameter module includes the Parameter class which is used to store
processing parameters.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['HdfKey']


class HdfKey(str):
    """
    Inherits from :py:class:`str`.
    
    A class used for referencing hdf keys.
    """
    def __new__(cls, text):
        _instance = super().__new__(cls, text)
        _instance.__hdf_fname = None
        return _instance

    @property
    def hdf_filename(self):
        """
        Get the filename of the associated hdf5 file.

        Returns
        -------
        str
            The filename of the associated hdf5 file.
        """
        return self.__hdf_fname

    @hdf_filename.setter
    def hdf_filename(self, txt):
        self.__hdf_fname = txt
