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
Module with utility functions asociated with Dectris detectors.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import h5py
import hdf5plugin
import numpy as np


def store_eiger_pixel_mask_from_master_file(master_filename, new_filename):
    """
    Store the pixel mask from a Dectris master Hdf5 file.

    Parameters
    ----------
    master_filename : str
        The filename for the master Hdf5 file.
    new_filename : str
        The filename for the output file.
    """
    _key = '/entry/instrument/detector/detectorSpecific/pixel_mask'
    with h5py.File(master_filename, 'r') as _file:
        _pixel_mask= _file[_key][()]
    _pixel_mask = _pixel_mask.astype(np.int8)
    np.save(new_filename, _pixel_mask)


def store_eiger_flat_field_from_master_file(master_filename, new_filename):
    """
    Store the flat field values from a Dectris master Hdf5 file.

    Parameters
    ----------
    master_filename : str
        The filename for the master Hdf5 file.
    new_filename : str
        The filename for the output file.
    """
    _key = '/entry/instrument/detector/detectorSpecific/flatfield'
    with h5py.File(master_filename, 'r') as _file:
        _flat_field= _file[_key][()]
    np.save(new_filename, _flat_field)
