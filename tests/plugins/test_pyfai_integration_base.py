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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import tempfile
import shutil
import os
import logging

import pyFAI
import numpy as np
from PyQt5 import QtCore

from pydidas.plugins import BasePlugin, pyFAIintegrationBase
from pydidas.core import get_generic_parameter
from pydidas.experiment import ExperimentalSetup


EXP_SETTINGS = ExperimentalSetup()

logger = logging.getLogger('pydidas_logger')
logger.setLevel(logging.ERROR)


class TestPyFaiIntegrationBase(unittest.TestCase):

    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._qsettings = QtCore.QSettings('Hereon', 'pydidas')
        self._qsettings_det_mask = self._qsettings.value('global/det_mask')
        self._qsettings.setValue('global/det_mask', '')
        self._shape = (50, 50)

    def tearDown(self):
        shutil.rmtree(self._temppath)
        self._qsettings.setValue('global/det_mask',
                                 self._qsettings_det_mask)

    def initialize_base_plugin(self, **kwargs):
        for key, value in [['rad_npoint', 900],
                           ['rad_unit', '2theta / deg'],
                           ['rad_use_range', False],
                           ['rad_range_lower', -1],
                           ['rad_range_upper', 1],
                           ['azi_npoint', 1],
                           ['azi_unit', 'chi / deg'],
                           ['azi_use_range', False],
                           ['azi_range_lower', -1],
                           ['azi_range_upper', 1],
                           ['int_method', 'CSR OpenCL']]:
            kwargs[key] = kwargs.get(key, value)
        plugin = pyFAIintegrationBase(**kwargs)
        return plugin

    def create_mask(self):
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=self._shape)
        _maskfilename = os.path.join(self._temppath, 'mask.npy')
        np.save(_maskfilename, _mask)
        return _maskfilename, _mask

    def test_init__plain(self):
        plugin = pyFAIintegrationBase()
        self.assertIsInstance(plugin, BasePlugin)

    def test_init__with_kwargs(self):
        _npoints = 7215421
        plugin = pyFAIintegrationBase(rad_npoint=_npoints)
        self.assertEqual(plugin.get_param_value('rad_npoint'), _npoints)

    def test_init__with_params(self):
        _npoints = 7215421
        _param = get_generic_parameter('rad_npoint')
        _param.value = _npoints
        plugin = pyFAIintegrationBase(_param)
        self.assertEqual(plugin.get_param_value('rad_npoint'), _npoints)

    def test_get_pyFAI_unit_from_param__plain(self):
        plugin = pyFAIintegrationBase(rad_unit='Q / nm^-1')
        self.assertEqual(plugin.get_pyFAI_unit_from_param('rad_unit'),
                         'q_nm^-1')

    def test_get_azimuthal_range_native__no_range(self):
        plugin = pyFAIintegrationBase(azi_use_range=False)
        _range = plugin.get_azimuthal_range_native()
        self.assertIsNone(_range)

    def test_get_azimuthal_range_native__lower_range_too_small(self):
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=-1,
                                      azi_range_upper=1)
        _range = plugin.get_azimuthal_range_native()
        self.assertIsNone(_range)

    def test_get_azimuthal_range_native__upper_range_too_small(self):
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=0,
                                      azi_range_upper=0)
        _range = plugin.get_azimuthal_range_native()
        self.assertIsNone(_range)

    def test_get_azimuthal_range_native__equal_boundaries(self):
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=12,
                                      azi_range_upper=12)
        _range = plugin.get_azimuthal_range_native()
        self.assertIsNone(_range)

    def test_get_azimuthal_range_native__upper_bound_lower(self):
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=15,
                                      azi_range_upper=12)
        _range = plugin.get_azimuthal_range_native()
        self.assertIsNone(_range)

    def test_get_azimuthal_range_native__correct(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=_range[0],
                                      azi_range_upper=_range[1])
        _newrange = plugin.get_azimuthal_range_native()
        self.assertEqual(_range, _newrange)

    def test_get_azimuthal_range_in_deg__empty(self):
        plugin = pyFAIintegrationBase(azi_use_range=False)
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertIsNone(_newrange)

    def test_get_azimuthal_range_in_deg__degree_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=_range[0],
                                      azi_range_upper=_range[1],
                                      azi_unit='chi / deg')
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertEqual(_range, _newrange)

    def test_get_azimuthal_range_in_deg__rad_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=_range[0],
                                      azi_range_upper=_range[1],
                                      azi_unit='chi / rad')
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertAlmostEqual(_newrange[0], _range[0] * 180 / np.pi)
        self.assertAlmostEqual(_newrange[1], _range[1] * 180 / np.pi)

    def test_get_azimuthal_range_in_rad__empty(self):
        plugin = pyFAIintegrationBase(azi_use_range=False)
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertIsNone(_newrange)

    def test_get_azimuthal_range_in_rad__degree_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=_range[0],
                                      azi_range_upper=_range[1],
                                      azi_unit='chi / deg')
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertAlmostEqual(_newrange[0] * 180 / np.pi, _range[0])
        self.assertAlmostEqual(_newrange[1] * 180 / np.pi, _range[1])

    def test_get_azimuthal_range_in_rad__rad_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(azi_use_range=True,
                                      azi_range_lower=_range[0],
                                      azi_range_upper=_range[1],
                                      azi_unit='chi / rad')
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertEqual(_range, _newrange)

    def test_get_radial_range__no_range(self):
        plugin = pyFAIintegrationBase(rad_use_range=False)
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__lower_range_too_small(self):
        plugin = pyFAIintegrationBase(rad_use_range=True,
                                      rad_range_lower=-1,
                                      rad_range_upper=1)
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__upper_range_too_small(self):
        plugin = pyFAIintegrationBase(rad_use_range=True,
                                      rad_range_lower=0,
                                      rad_range_upper=0)
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__equal_boundaries(self):
        plugin = pyFAIintegrationBase(rad_use_range=True,
                                      rad_range_lower=12,
                                      rad_range_upper=12)
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__upper_bound_lower(self):
        plugin = pyFAIintegrationBase(rad_use_range=True,
                                      rad_range_lower=15,
                                      rad_range_upper=12)
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__correct(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(rad_use_range=True,
                                      rad_range_lower=_range[0],
                                      rad_range_upper=_range[1])
        _newrange = plugin.get_radial_range()
        self.assertEqual(_range, _newrange)

    def test_calculate_result_shape(self):
        _range = (1234, 789)
        plugin = pyFAIintegrationBase(rad_npoint=_range[0],
                                      azi_npoint=_range[1])
        plugin.output_data_dim = 1
        with self.assertRaises(NotImplementedError):
            plugin.calculate_result_shape()

    def test_load_and_store_mask__local_mask_value(self):
        _maskfilename, _mask = self.create_mask()
        plugin = pyFAIintegrationBase()
        plugin.set_param_value('det_mask', _maskfilename)
        plugin.load_and_store_mask()
        self.assertTrue((plugin._mask == _mask).all())

    def test_load_and_store_mask__q_settings(self):
        _maskfilename, _mask = self.create_mask()
        self._qsettings.setValue('global/det_mask', _maskfilename)
        plugin = pyFAIintegrationBase()
        plugin._original_image_shape = (123, 50)
        plugin.load_and_store_mask()
        self.assertTrue(np.equal(plugin._mask, _mask).all())

    def test_load_and_store_mask__wrong_local_mask_and_q_settings(self):
        _maskfilename, _mask = self.create_mask()
        self._qsettings.setValue('global/det_mask', _maskfilename)
        plugin = pyFAIintegrationBase()
        plugin._original_image_shape = (123, 50)
        plugin.set_param_value('det_mask',
                               os.path.join(self._temppath, 'no_mask.npy'))
        plugin.load_and_store_mask()
        self.assertTrue(np.equal(plugin._mask, _mask).all())

    def test_load_and_store_mask__no_mask(self):
        plugin = pyFAIintegrationBase()
        plugin._original_image_shape = (123, 45)
        plugin.load_and_store_mask()
        self.assertIsNone(plugin._mask)

    def test_pre_execute(self):
        plugin = pyFAIintegrationBase()
        plugin._original_image_shape = (123, 45)
        plugin.pre_execute()
        self.assertIsInstance(plugin._ai,
                              pyFAI.azimuthalIntegrator.AzimuthalIntegrator)


if __name__ == "__main__":
    unittest.main()
