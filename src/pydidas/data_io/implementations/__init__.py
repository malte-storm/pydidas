# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
The data__io.implementations package includes imports/exporters for data
in different formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import  items from modules:
# need to import all modules to have the IO classes
# registered in the IOManager metaclass
from . import (
    fabio_io,
    hdf5_io,
    io_exporter_matplotlib,
    jpeg_io,
    numpy_io,
    png_io,
    raw_io,
    tiff_io,
)
from .io_base import *


__all__ = io_base.__all__

# Clean up the namespace:
del (
    fabio_io,
    hdf5_io,
    io_exporter_matplotlib,
    jpeg_io,
    numpy_io,
    png_io,
    raw_io,
    tiff_io,
)
