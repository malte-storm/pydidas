# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Module with the PyFAI2dIntegration Plugin which allows to integrate diffraction
patterns into a 2D radial/azimuthal map.
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConvertToDSpacing"]


import numpy as np

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import Dataset, get_generic_param_collection, get_generic_parameter
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_IMAGE
from pydidas.plugins import ProcPlugin


class ConvertToDSpacing(ProcPlugin):
    """
    Convert Q, r or 2θ data from an integration plugin to d-spacing.

    WARNING: pydidas is not yet capable of displaying non-uniform data.
    """

    plugin_name = "Convert to d-spacing"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_IMAGE
    default_params = get_generic_param_collection("d_spacing_unit")
    input_data_dim = -1
    output_data_dim = -1

    def __init__(self, *args, **kwargs):
        self._EXP = kwargs.pop("diffraction_exp", DiffractionExperimentContext())
        super().__init__(*args, **kwargs)

    def pre_execute(self):
        self._lambda = self._EXP.get_param_value("xray_wavelength")
        self._detector_dist = self._EXP.get_param_value("detector_dist")

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Convert Q, r, or 2θ data from an integration plugin to d-spacing.

        Parameters:
            data : pydidas.core.Dataset
                The image / frame data.
            **kwargs : dict
                Any calling keyword arguments.

        Returns:
            data : pydidas.core.Dataset
                The converted data.
            kwargs : dict
                Any calling kwargs, appended by any changes in the function.
        """
        for axis, label in data.axis_labels.items():
            if (
                f"{label} / {data.axis_units[axis]}"
                in get_generic_parameter("rad_unit").choices
            ):
                _range = data.axis_ranges[axis]
                match label:
                    case "Q":
                        if data.axis_units[axis] == "nm^-1":
                            _range = _range / 10
                        _range = (2 * np.pi) / _range
                    case "r":
                        _range = self._lambda / (
                            2
                            * np.sin(
                                np.arctan(_range / (self._detector_dist * 1e3)) / 2
                            )
                        )
                    case "2theta":
                        if data.axis_units[axis] == "deg":
                            _range = np.radians(_range)
                        _range = self._lambda / (2 * np.sin(_range / 2))
                if self.get_param_value("d_spacing_unit") == "nm":
                    _range /= 10
                    data.update_axis_unit(axis, "nm")
                else:
                    data.update_axis_unit(axis, "A")
                data.update_axis_range(axis, _range)
                data.update_axis_label(axis, "d-spacing")
        return data, kwargs
