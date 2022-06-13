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
Module with the FrameLoader Plugin which can be used to load files with
single images in each, e.g. tiff files or numpy files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FrameLoader"]


from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core import get_generic_param_collection
from pydidas.managers import FilelistManager
from pydidas.plugins import InputPlugin
from pydidas.data_io import import_data
from pydidas.core.utils import copy_docstring


class FrameLoader(InputPlugin):
    """
    Load data frames from files with a single image in each, for example tif
    or cif files.

    This class is designed to load data from a series of files. The file
    series is defined through the first and last file and file stepping.
    Filesystem checks can be disabled using the live_processing keyword but
    are enabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    first_file : Union[str, pathlib.Path]
        The name of the first file in the file series.
    last_file : Union[str, pathlib.Path]
        The name of the last file in the file series.
    images_per_file : int
        The number of images per file.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """

    plugin_name = "Single frame loader"
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = get_generic_param_collection(
        "first_file", "last_file", "live_processing", "file_stepping"
    )
    input_data_dim = None
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_param_value("live_processing", False)
        self._file_manager = FilelistManager(
            *self.get_params(
                "first_file", "last_file", "live_processing", "file_stepping"
            )
        )

    def pre_execute(self):
        """
        Prepare loading of images from a series of files.
        """
        self._file_manager.update()
        self._image_metadata.update()

    def execute(self, index, **kwargs):
        """
        Execute the plugin and load an image from a file.

        Parameters
        ----------
        index : int
            The index for the image.
        **kwargs : dict
            Any optional keyword arguments for reading the file.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data in a Dataset.
        kwargs : dict
            Any input kwargs are returned to be passed on to the next plugin.
        """
        _fname = self.get_filename(index)
        kwargs["binning"] = self.get_param_value("binning")
        kwargs["roi"] = self._image_metadata.roi
        _data = import_data(_fname, **kwargs)
        return _data, kwargs

    @copy_docstring(InputPlugin)
    def get_filename(self, index):
        """
        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        return self._file_manager.get_filename(index)