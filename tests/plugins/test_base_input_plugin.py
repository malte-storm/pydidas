# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import tempfile
import shutil
import h5py
import os

import numpy as np

from pydidas.unittest_objects.dummy_plugin_collection import (
    create_plugin_class)

from pydidas.plugins import InputPlugin
from pydidas.constants import INPUT_PLUGIN
from pydidas.core import Parameter
from pydidas.core import get_generic_parameter
from pydidas.apps.app_utils import ImageMetadataManager
from pydidas._exceptions import AppConfigError

class TestBaseInputPlugin(unittest.TestCase):

    def setUp(self):
        self._datashape = (130, 140)
        self._testpath = tempfile.mkdtemp()
        self._fname = os.path.join(self._testpath, 'test.h5')
        with h5py.File(self._fname, 'w') as f:
            f['entry/data/data'] = np.ones((15,) + self._datashape)

    def tearDown(self):
        shutil.rmtree(self._testpath)

    def test_create_base_plugin(self):
        plugin = create_plugin_class(0, INPUT_PLUGIN)
        self.assertIsInstance(plugin(), InputPlugin)

    def test_class_atributes(self):
        plugin = create_plugin_class(0, INPUT_PLUGIN)
        for att in ('basic_plugin', 'plugin_type', 'plugin_name',
                    'default_params', 'generic_params', 'input_data_dim',
                    'output_data_dim'):
            self.assertTrue(hasattr(plugin, att))

    def test_class_generic_params(self):
        plugin = create_plugin_class(0, INPUT_PLUGIN)
        for att in ('use_roi', 'roi_xlow', 'roi_xhigh', 'roi_ylow',
                    'roi_yhigh', 'binning'):
            _param = plugin.generic_params.get_param(att)
            self.assertIsInstance(_param, Parameter)

    def test_setup_image_metadata_manager__with_firstfile(self):
        _class = create_plugin_class(0, INPUT_PLUGIN, use_filename=False)
        plugin = _class()
        plugin.set_param_value('first_file', self._fname)
        plugin._InputPlugin__setup_image_magedata_manager()
        self.assertIsInstance(plugin._image_metadata, ImageMetadataManager)
        self.assertFalse(plugin._image_metadata.get_param_value('use_filename'))

    def test_setup_image_metadata_manager__with_filename(self):
        _class = create_plugin_class(0, INPUT_PLUGIN, use_filename=True)
        plugin = _class()
        plugin.set_param_value('filename', self._fname)
        plugin._InputPlugin__setup_image_magedata_manager()
        self.assertIsInstance(plugin._image_metadata, ImageMetadataManager)
        self.assertTrue(plugin._image_metadata.get_param_value('use_filename'))

    def test_setup_image_metadata_manager__with_firstfile_and_filename(self):
        _class = create_plugin_class(0, INPUT_PLUGIN, use_filename=True)
        plugin = _class()
        _class.default_params.add_param(get_generic_parameter('first_file'))
        with self.assertRaises(AppConfigError):
            plugin._InputPlugin__setup_image_magedata_manager()

    def test_setup_image_metadata_manager__with_different_hdf5_key(self):
        _class = create_plugin_class(0, INPUT_PLUGIN, use_filename=True)
        _class.default_params.add_param(get_generic_parameter('hdf5_key'))
        plugin = _class()
        with h5py.File(self._fname, 'w') as f:
            f['other_entry/dataset/_data'] = np.ones((15,) + self._datashape)
        plugin.set_param_value('hdf5_key', 'other_entry/dataset/_data')
        plugin.set_param_value('filename', self._fname)
        plugin._InputPlugin__setup_image_magedata_manager()
        plugin._image_metadata.update()
        plugin.calculate_result_shape()
        self.assertEqual(plugin.result_shape, self._datashape)

    def test_calculate_result_shape(self):
        _class = create_plugin_class(0, INPUT_PLUGIN, use_filename=True)
        plugin = _class()
        plugin.set_param_value('filename', self._fname)
        plugin.calculate_result_shape()
        self.assertEqual(self._datashape, plugin.result_shape)


if __name__ == "__main__":
    unittest.main()
