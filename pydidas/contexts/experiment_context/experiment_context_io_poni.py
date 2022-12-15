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
Module with the ExperimentContextIoPoni class which is used to import
ExperimentContext metadata from a pyFAI poni file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ExperimentContextIoPoni"]

import pyFAI

from ...core.constants import LAMBDA_IN_M_TO_E
from .experiment_context_io_base import ExperimentContextIoBase
from .experiment_context import ExperimentContext


EXP = ExperimentContext()


class ExperimentContextIoPoni(ExperimentContextIoBase):
    """
    Base class for WorkflowTree exporters.
    """

    extensions = ["poni"]
    format_name = "PONI"

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Write the ExperimentalTree to a pyFAI style poni file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _pdata = {}
        for key in ["rot1", "rot2", "rot3", "poni1", "poni2"]:
            _pdata[key] = EXP.get_param_value(f"detector_{key}")
        _pdata["detector"] = EXP.get_param_value("detector_name")
        _pdata["distance"] = EXP.get_param_value("detector_dist")
        if (
            _pdata["detector"] in pyFAI.detectors.Detector.registry
            and _pdata["detector"] != "detector"
        ):
            _pdata["detector_config"] = {}
        else:
            _pdata["detector_config"] = dict(
                pixel1=(1e-6 * EXP.get_param_value("detector_pxsizey")),
                pixel2=(1e-6 * EXP.get_param_value("detector_pxsizex")),
                max_shape=(
                    EXP.get_param_value("detector_npixy"),
                    EXP.get_param_value("detector_npixx"),
                ),
            )
        _pdata["wavelength"] = EXP.get_param_value("xray_wavelength") * 1e-10
        pfile = pyFAI.io.ponifile.PoniFile()
        pfile.read_from_dict(_pdata)
        with open(filename, "w") as stream:
            pfile.write(stream)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the ExperimentContext from a YAML file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        geo = pyFAI.geometry.Geometry().load(filename)
        cls.imported_params = {}
        cls._update_detector_from_pyFAI(geo.detector)
        cls._update_geometry_from_pyFAI(geo)
        cls._verify_all_entries_present()
        cls._write_to_exp_settings()

    @classmethod
    def _update_detector_from_pyFAI(cls, det):
        """
        Update the detector information from a pyFAI Detector instance.
        """
        if not isinstance(det, pyFAI.detectors.Detector):
            raise TypeError(
                f'Object "{det} (type {type(det)} is not a '
                "pyFAI.detectors.Detector instance."
            )
        for key, value in [
            ["detector_name", det.name],
            ["detector_npixx", det.shape[1]],
            ["detector_npixy", det.shape[0]],
            ["detector_pxsizex", 1e6 * det.pixel2],
            ["detector_pxsizey", 1e6 * det.pixel1],
        ]:
            cls.imported_params[key] = value

    @classmethod
    def _update_geometry_from_pyFAI(cls, geo):
        """
        Update the geometry information from a pyFAI Geometry instance.
        """
        if not isinstance(geo, pyFAI.geometry.Geometry):
            raise TypeError(
                f'Object "{geo} (type {type(geo)} is not a '
                "pyFAI.geometry.Geometry instance."
            )
        cls.imported_params["xray_wavelength"] = geo.wavelength * 1e10
        cls.imported_params["xray_energy"] = LAMBDA_IN_M_TO_E / geo.wavelength
        _geodict = geo.getPyFAI()
        for key in [
            "detector_dist",
            "detector_poni1",
            "detector_poni2",
            "detector_rot1",
            "detector_rot2",
            "detector_rot3",
        ]:
            cls.imported_params[key] = _geodict[key.split("_")[1]]