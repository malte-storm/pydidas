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
The generic_params_isettings module holds all the required data to create generic
Parameters for the global pydidas settings
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GENERIC_PARAMS_SETTINGS"]


GENERIC_PARAMS_SETTINGS = {
    "mp_n_workers": {
        "type": int,
        "default": 4,
        "name": "Number of MP workers",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of multiprocessing workers. Note that this number should "
            "not be set too high for two reasons:\n1. File reading processes "
            "interfere with each other if too many are active at once.\n2. pyFAI "
            "already inherently uses parallelization and you can only gain limited "
            "performance increases for multiple parallel processes."
        ),
    },
    "shared_buffer_size": {
        "type": float,
        "default": 100,
        "name": "Shared buffer size limit",
        "choices": None,
        "unit": "MB",
        "allow_None": False,
        "tooltip": (
            "A shared buffer is used to efficiently transport data between the "
            "main App and multiprocessing Processes. This buffer must be large "
            "enough to store at least one instance of all result data."
        ),
    },
    "shared_buffer_max_n": {
        "type": int,
        "default": 20,
        "name": "Buffer dataframe limit",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The maximum number of datasets in the buffer. A dataset consists of "
            "all results for one frame. For performance reasons, the buffer should "
            "not be too large."
        ),
    },
    "max_image_size": {
        "type": float,
        "default": 100,
        "name": "Maximum image size",
        "choices": None,
        "unit": "Mpx",
        "allow_None": False,
        "tooltip": "The maximum size (in megapixels) of images.",
    },
    "use_global_det_mask": {
        "type": bool,
        "default": True,
        "name": "Use global detector mask",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Flag to use the global detector mask file and value. If False, no "
            "detector mask will be used."
        ),
    },
    "det_mask": {
        "type": "Path",
        "default": "",
        "name": "Detector mask file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The path to the detector mask file.",
    },
    "det_mask_val": {
        "type": float,
        "default": 0,
        "name": "Mask display value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The value to be used for the pixels masked on the detector. Note that "
            "this value will only be used for displaying the images. For pyFAI "
            "integration, the pixels will be fully masked and not be included."
        ),
    },
    "mosaic_border_width": {
        "type": int,
        "default": 0,
        "name": "Mosaic tiling border width",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The width of the border inserted between adjacent frames"
            " in the mosaic creation."
        ),
    },
    "mosaic_border_value": {
        "type": float,
        "default": 0,
        "name": "Mosaic border value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The value to be put in the border pixels in mosaics.",
    },
    "run_type": {
        "type": str,
        "default": "Process in GUI",
        "name": "Run type",
        "choices": ["Process in GUI", "Command line"],
        "unit": "",
        "allow_None": False,
        "tooltip": ("Specify how the processing shall be performed."),
    },
    "plugin_path": {
        "type": str,
        "default": "",
        "name": "Plugin paths",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The paths to all plugin locations. Individual entries are"
            ' separated by a double semicolon ";;".'
        ),
    },
    "plot_update_time": {
        "type": float,
        "default": 1.0,
        "name": "Plot update time",
        "choices": None,
        "allow_None": False,
        "unit": "s",
        "tooltip": (
            "The delay before any plot updates will be processed. This"
            " will prevent multiple frequent update of plots."
        ),
    },
    "histogram_outlier_fraction": {
        "type": float,
        "default": 0.07,
        "name": "Histogram outlier fraction",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The fraction of pixels which will be ignored when cropping the "
            "histogram for 2d plots. A value of 0.07 will mask all sensor gaps in "
            "the Eiger."
        ),
    },
}