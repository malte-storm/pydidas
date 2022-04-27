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
Module with the FabioIo class for reading ESRF-type images, e.g. EDF.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import fabio

from ...core.constants import FABIO_EXTENSIONS
from ...core import Dataset
from .io_base import IoBase


class FabioIo(IoBase):
    """IObase implementation for files supported by FabIO (e.g. EDF)."""
    extensions_export = []
    extensions_import = FABIO_EXTENSIONS
    format_name = 'FabIO reader'
    dimensions = [2]

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        """
        Read an image from a FabIO-supported file format.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        roi : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.
        returnType : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The rebinning factor to be applied to the image. The default
            is 1.

        Returns
        -------
        image : pydidas.core.Dataset
            The image in form of a Dataset (with embedded metadata)
        """
        with fabio.open(filename) as _file:
            _data = _file.data
            _header = _file.header
        cls._data = Dataset(_data, metadata=_header)
        return cls.return_data(**kwargs)
