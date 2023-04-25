# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the pyFAIintegrationBase Plugin which is inherited by all
integration plugins using pyFAI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["pyFAIintegrationBase", "pyFAI_UNITS", "pyFAI_METHOD"]


import multiprocessing as mp
import os
import pathlib

import numpy as np
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
from silx.opencl.common import OpenCL

from ..contexts import DiffractionExperimentContext
from ..core import UserConfigError, get_generic_param_collection
from ..core.constants import GREEK_ASCII_TO_UNI, PROC_PLUGIN, PROC_PLUGIN_IMAGE
from ..core.utils import pydidas_logger, rebin2d
from ..data_io import import_data
from ..widgets.plugin_config_widgets import PyfaiIntegrationConfigWidget
from .base_proc_plugin import ProcPlugin


logger = pydidas_logger()


pyFAI_UNITS = {
    "Q / nm^-1": "q_nm^-1",
    "Q / A^-1": "q_A^-1",
    "2theta / deg": "2th_deg",
    "2theta / rad": "2th_rad",
    "r / mm": "r_mm",
    "chi / deg": "chi_deg",
    "chi / rad": "chi_rad",
}

pyFAI_METHOD = {
    "CSR": ("bbox", "csr", "cython"),
    "CSR OpenCL": ("bbox", "csr", "opencl"),
    "CSR full": ("full", "csr", "cython"),
    "CSR full OpenCL": ("full", "csr", "opencl"),
    "LUT": ("bbox", "lut", "cython"),
    "LUT OpenCL": ("bbox", "lut", "opencl"),
    "LUT full": ("full", "lut", "cython"),
    "LUT full OpenCL": ("full", "lut", "opencl"),
}

OCL = OpenCL()

PI_STR = GREEK_ASCII_TO_UNI["pi"]


class pyFAIintegrationBase(ProcPlugin):
    """
    Provide basic functionality for the concrete integration plugins.
    """

    plugin_name = "PyFAI integration base"
    basic_plugin = True
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_IMAGE
    default_params = get_generic_param_collection(
        "rad_npoint",
        "rad_unit",
        "rad_use_range",
        "rad_range_lower",
        "rad_range_upper",
        "azi_npoint",
        "azi_unit",
        "azi_use_range",
        "azi_range_lower",
        "azi_range_upper",
        "int_method",
    )
    input_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."
    new_dataset = True
    has_unique_parameter_config_widget = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ai = None
        self._ai_params = {}
        self._exp_hash = -1
        self._EXP = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        self._mask = None

    def pre_execute(self):
        """
        Check and load the mask and set up the AzimuthalIntegrator.
        """
        self.load_and_set_mask()
        if self._exp_hash != hash(self._EXP):
            _lambda_in_A = self._EXP.get_param_value("xray_wavelength")
            self._ai = AzimuthalIntegrator(
                dist=self._EXP.get_param_value("detector_dist"),
                poni1=self._EXP.get_param_value("detector_poni1"),
                poni2=self._EXP.get_param_value("detector_poni2"),
                rot1=self._EXP.get_param_value("detector_rot1"),
                rot2=self._EXP.get_param_value("detector_rot2"),
                rot3=self._EXP.get_param_value("detector_rot3"),
                detector=self._EXP.get_detector(),
                wavelength=1e-10 * _lambda_in_A,
            )
        if self._mask is not None:
            self._ai.set_mask(self._mask)
        self._adjust_integration_discontinuity()
        self._prepare_pyfai_method()

    def load_and_set_mask(self):
        """
        Load and store the mask.

        If defined (and the file exists), the locally defined detector mask
        Parameter will be used. If not, the global QSetting detector mask
        will be used.
        """
        self._mask = None
        _mask_file = self._EXP.get_param_value("detector_mask_file")
        if _mask_file != pathlib.Path():
            if os.path.isfile(_mask_file):
                self._mask = import_data(_mask_file)
            else:
                raise UserConfigError(
                    f"Cannot load detector mask: No file with the name \n{_mask_file}"
                    "\nexists."
                )
        if self._mask is not None and len(self._legacy_image_ops) > 0:
            _roi, _bin = self.get_single_ops_from_legacy()
            self._mask = np.where(rebin2d(self._mask[_roi], _bin) > 0, 1, 0)

    def _prepare_pyfai_method(self):
        """
        Prepare the method name and select OpenCL device if multiple devices
        present.
        """
        _method = pyFAI_METHOD[self.get_param_value("int_method")]
        self._config["method"] = _method
        if _method[2] != "opencl":
            return
        _name = mp.current_process().name
        _platforms = [_platform.name for _platform in OCL.platforms]
        if "NVIDIA CUDA" in _platforms and _name.startswith("pydidas_"):
            _index = int(_name.split("-")[1])
            _platform = OCL.get_platform("NVIDIA CUDA")
            _n_device = len(_platform.devices)
            _device = _index % _n_device
            _method = _method + ((_platform.id, _device),)
            self._config["method"] = _method

    def calculate_result_shape(self):
        """
        Get the shape of the integrated dataset to set up the CRS / LUT.

        Returns
        -------
        Union[int, tuple]
            The new shape. For 1-dimensional integration, a single integer is
            returned. For 2-dimensional integrations a tuple of two integers
            is returned.
        """
        raise NotImplementedError(
            "Must be implemented by the concrete pyFAI integration plugin"
        )

    def get_azimuthal_range_in_rad(self):
        """
        Get the azimuthal range from the Parameters in radians.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "deg" in self.get_param_value("azi_unit"):
                _range = (np.pi / 180 * _range[0], np.pi / 180 * _range[1])
        return _range

    def get_azimuthal_range_in_deg(self):
        """
        Get the azimuthal range from the Parameters in degree.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "rad" in self.get_param_value("azi_unit"):
                _range = (180 / np.pi * _range[0], 180 / np.pi * _range[1])
        return _range

    def get_azimuthal_range_native(self):
        """
        Get the azimuthal range from the Parameters in native units.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        if self.get_param_value("azi_use_range") == "Specify azimuthal range":
            self.modulate_and_store_azi_range()
            _low = self.get_param_value("azi_range_lower")
            _high = self.get_param_value("azi_range_upper")
            if _low == _high:
                return None
            return (
                self.get_param_value("azi_range_lower"),
                self.get_param_value("azi_range_upper"),
            )
        return None

    def _adjust_integration_discontinuity(self):
        """
        Check the position of the integration discontinuity and adjust it according
        to the integration bounds.
        """
        _range = self.get_azimuthal_range_in_rad()
        if _range is None:
            return
        _low, _high = _range
        if _high - _low > 2 * np.pi:
            raise UserConfigError(
                "The integration range is larger than a full circle! "
                "Please adjust the boundaries and try again."
            )
        if _low >= 0:
            if self._ai.chiDiscAtPi:
                self._ai.reset()
            self._ai.setChiDiscAtZero()
        elif _low < 0 and _high <= np.pi:
            if not self._ai.chiDiscAtPi:
                self._ai.reset()
            self._ai.setChiDiscAtPi()
        else:
            self._raise_range_error(_low, _high)

    def modulate_and_store_azi_range(self):
        """
        Try to modulate the azimuthal range to be compatible with pyFAI.
        """
        _factor = 1 if "rad" in self.get_param_value("azi_unit") else np.pi / 180
        _lower = _factor * self.get_param_value("azi_range_lower")
        _upper = _factor * self.get_param_value("azi_range_upper")
        if _upper > 2 * np.pi:
            _lower = np.mod(_lower, 2 * np.pi)
            _upper = np.mod(_upper, 2 * np.pi)
        if _lower > _upper:
            _lower -= 2 * np.pi
        if _lower < -np.pi:
            _lower = np.mod(_lower + np.pi, 2 * np.pi) - np.pi
            _upper = np.mod(_upper + np.pi, 2 * np.pi) - np.pi
        if (
            (_lower < 0 and _upper >= np.pi)
            or _lower > _upper
            or (_upper - _lower > 2 * np.pi)
        ):
            self._raise_range_error(_lower, _upper)
        self.set_param_value("azi_range_lower", _lower / _factor)
        self.set_param_value("azi_range_upper", _upper / _factor)

    def _raise_range_error(self, low, high):
        """
        Raise a UserConfigError that the specified bounds are invalid.

        Parameters
        ----------
        low : float
            The lower bound.
        high : float
            The upper bound.
        """
        _intervals = (
            f"[-{PI_STR}, {PI_STR}] or [0, 2*{PI_STR}]"
            if "rad" in self.get_param_value("azi_unit")
            else "[-180\u00B0, 180\u00B0] or [0\u00B0, 360\u00B0]"
        )
        low = np.round(low, 5)
        high = np.round(high, 5)
        raise UserConfigError(
            f"The chosen integration range ({low}, {high}) cannot be processed "
            "because it cannot be represented in pyFAI. The range must be either "
            f"in the interval {_intervals}."
        )

    def is_range_valid(self):
        """
        Check whether the plugin's range is valid.

        Parameters
        ----------
        azi_range : tuple
            The azimuthal range.

        Returns
        -------
        bool
            Flag whether the range is valid or not.
        """
        try:
            self.modulate_and_store_azi_range()
        except UserConfigError:
            return False
        _range = self.get_azimuthal_range_in_rad()
        if _range is None:
            return True
        _low, _high = _range
        if _low > _high:
            _low = np.mod(_low + np.pi, 2 * np.pi) - np.pi
            _high = np.mod(_high + np.pi, 2 * np.pi) - np.pi
        if -np.pi <= _low < 0:
            return _low < _high <= np.pi + 1e-7
        return 0 <= _low <= _high <= 2 * np.pi + 1e-7

    def get_pyFAI_unit_from_param(self, param_name):
        """
        Get the unit of the Parameter called param_name in pyFAI notation.

        Parameters
        ----------
        param_name : str
            The reference key of the Parameter with the unit.

        Returns
        -------
        str
            The unit in pyFAI notation.
        """
        return pyFAI_UNITS[self.get_param_value(param_name)]

    def execute(self, data, **kwargs):
        """
        To be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def get_parameter_config_widget(self):
        """
        Get the unique configuration widget associated with this Plugin.

        Returns
        -------
        QtWidgets.QWidget
            The unique ParameterConfig widget
        """
        return PyfaiIntegrationConfigWidget(self)

    def get_radial_range(self):
        """
        Get the radial range from the Parameters.

        If use_radial_range is True and both the lower and upper range limits
        are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The radial range for the pyFAI integration.
        """
        if self.get_param_value("rad_use_range") == "Specify radial range":
            _lower = self.get_param_value("rad_range_lower")
            _upper = self.get_param_value("rad_range_upper")
            if 0 <= _lower < _upper:
                return (_lower, _upper)
            logger.warning(
                "Warning: Radial range was not correct and has been ignored."
            )
        return None

    def get_radial_range_as_r(self):
        """
        Get the radial range as radius in mm.

        Returns
        -------
        range : Union[None, tuple]
            If no range has been set, returns None. Otherwise, the range limits are
            given as tuple.
        """
        _range = self.get_radial_range_as_2theta(unit="rad")
        if _range is None:
            return None
        _dist = self._EXP.get_param_value("detector_dist") * 1e3
        return (_dist * np.tan(_range[0]), _dist * np.tan(_range[1]))

    def get_radial_range_as_q(self):
        """
        Get the radial range as q in nm^-1.

        Returns
        -------
        range : Union[None, tuple]
            If no range has been set, returns None. Otherwise, the range limits are
            given as tuple.
        """
        _range = self.get_radial_range_as_2theta(unit="rad")
        if _range is None:
            return None
        _lambda = self._EXP.get_param_value("xray_wavelength") * 1e-10
        _q = (4 * np.pi / _lambda) * np.sin(np.asarray(_range) / 2) * 1e-9
        return tuple(_q)

    def get_radial_range_as_2theta(self, unit="deg"):
        """
        Get the radial range converted to 2 theta.

        Parameters
        ----------
        unit : str, optional
            The unit of the range. Must be either "rad" or "deg". The default is "deg".

        Returns
        -------
        range : Union[None, tuple]
            If no range has been set, returns None. Otherwise, the range limits are
            given as tuple.
        """
        if not self.get_param_value("rad_use_range"):
            return None
        _low = np.pi / 180 * self.get_param_value("rad_range_lower")
        _high = np.pi / 180 * self.get_param_value("rad_range_upper")
        _unit = self.get_param_value("rad_unit")
        _factor = 1 if unit == "rad" else 180 / np.pi
        if unit == "Q / nm^-1":
            _lambda = self._EXP.get_param_value("xray_wavelength") * 1e-10
            _low = 2 * np.arcsin((_low * 1e9 * _lambda) / (4 * np.pi))
            _high = 2 * np.arcsin((_high * 1e9 * _lambda) / (4 * np.pi))
        elif _unit == "r / mm":
            _dist = self._EXP.get_param_value("detector_dist")
            _low = np.arctan(_low * 1e-3 / _dist)
            _high = np.arctan(_high * 1e-3 / _dist)
        return _low * _factor, _high * _factor
