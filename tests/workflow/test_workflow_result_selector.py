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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import os
import shutil
import tempfile
from numbers import Real

import numpy as np
import h5py

from pydidas.core import Dataset, get_generic_parameter, Parameter, AppConfigError
from pydidas.experiment import ScanSetup
from pydidas.unittest_objects import DummyProc, DummyLoader
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.workflow.result_savers import WorkflowResultSaverMeta
from pydidas.workflow.workflow_results_selector import WorkflowResultsSelector

SCAN = ScanSetup()
TREE = WorkflowTree()
RES = WorkflowResults()
SAVER = WorkflowResultSaverMeta


class TestWorkflowResultSelector(unittest.TestCase):

    def setUp(self):
        self.set_up_scan()
        self.set_up_tree()
        RES.clear_all_results()
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def set_up_scan(self):
        self._scan_n = (5, 2, 3)
        self._scan_offsets = (-3, 0, 3.2)
        self._scan_delta = (0.1, 1, 12)
        self._scan_unit = ('m', 'mm', 'm')
        self._scan_label = ('Test', 'Dir 2', 'other dim')
        SCAN.set_param_value('scan_dim', len(self._scan_n))
        for _dim in range(len(self._scan_n)):
            SCAN.set_param_value(f'n_points_{_dim + 1}', self._scan_n[_dim])
            SCAN.set_param_value(f'offset_{_dim + 1}',
                                 self._scan_offsets[_dim])
            SCAN.set_param_value(f'delta_{_dim + 1}', self._scan_delta[_dim])
            SCAN.set_param_value(f'unit_{_dim + 1}', self._scan_unit[_dim])
            SCAN.set_param_value(f'scan_dir_{_dim + 1}',
                                 self._scan_label[_dim])

    def set_up_tree(self):
        self._result1_shape = (12, 27)
        self._result2_shape = (3, 3, 5)
        TREE.clear()
        TREE.create_and_add_node(DummyLoader())
        TREE.nodes[0].plugin.set_param_value('image_height',
                                             self._result1_shape[0])
        TREE.nodes[0].plugin.set_param_value('image_width',
                                             self._result1_shape[1])
        TREE.create_and_add_node(DummyProc())
        TREE.create_and_add_node(DummyProc(), parent=TREE.root)
        TREE.prepare_execution()
        TREE.nodes[2]._result_shape = self._result2_shape

    def populate_WorkflowResults(self):
        RES.update_shapes_from_scan_and_workflow()
        _results = {
            1: Dataset(
                np.random.random(self._result1_shape),
                axis_units=['m', 'mm'], axis_labels=['dim1', 'dim 2'],
                axis_ranges=[np.arange(self._result1_shape[0]),
                             37 - np.arange(self._result1_shape[1])]),
            2: Dataset(np.random.random(self._result2_shape),
                       axis_units=['m', 'Test', None],
                       axis_labels=['dim1', '2nd dim', 'dim #3'],
                       axis_ranges=[12 + np.arange(self._result1_shape[0]),
                                    None, None])
            }
        RES.store_results(0, _results)
        RES._WorkflowResults__composites[1][:] = (
            np.random.random(self._scan_n + self._result1_shape) + 0.0001)
        RES._WorkflowResults__composites[2][:] = (
            np.random.random(self._scan_n + self._result2_shape) + 0.0001)

    def generate_test_datasets(self):

        return _results


    def test_unitttest_setUp(self):
        ...

    def test_populate_WorkflowResults(self):
        self.populate_WorkflowResults()
        for _index in [1, 2]:
            _res = RES.get_results(_index)
            self.assertEqual(
                _res.shape,
                self._scan_n + getattr(self, f'_result{_index}_shape'))
            self.assertTrue(np.alltrue(_res > 0))

    def test_init(self):
        obj = WorkflowResultsSelector()
        self.assertIsInstance(obj, WorkflowResultsSelector)
        self.assertTrue('_selection' in obj.__dict__)
        self.assertTrue('_npoints' in obj.__dict__)
        self.assertTrue('_active_node' in obj.__dict__)

    def test_init__with_param(self):
        _param = Parameter('result_n_dim', int, 124)
        obj = WorkflowResultsSelector(_param)
        self.assertIsInstance(obj, WorkflowResultsSelector)
        self.assertEqual(_param, obj.get_param('result_n_dim'))

    def test_reset(self):
        obj = WorkflowResultsSelector()
        obj._active_node = 12
        obj._selection = [1, 2, 3]
        obj.reset()
        self.assertIsNone(obj._selection)
        self.assertEqual(obj._active_node, -1)

    def test_check_and_create_params_for_slice_selection(self):
        self.populate_WorkflowResults()
        _ndim = len(self._scan_n) + len(self._result2_shape)
        obj = WorkflowResultsSelector()
        obj._active_node = 2
        obj._check_and_create_params_for_slice_selection()
        for _dim in range(_ndim):
            self.assertIn(f'data_slice_{_dim}', obj.params)
        self.assertNotIn(f'data_slice_{_ndim}', obj.params)

    def test_calc_and_store_ndim_of_results__no_timeline(self):
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj._active_node = 2
        obj._calc_and_store_ndim_of_results()
        self.assertEqual(obj._config['result_ndim'],
                         len(self._scan_n) + len(self._result2_shape))

    def test_calc_and_store_ndim_of_results__with_timeline(self):
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj._active_node = 2
        obj.set_param_value('use_scan_timeline', True)
        obj._calc_and_store_ndim_of_results()
        self.assertEqual(obj._config['result_ndim'],
                         1 + len(self._result2_shape))

    def test_select_active_node(self):
        _node = 2
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        self.assertEqual(obj._active_node, _node)
        self.assertIsNotNone(obj._config.get('result_ndim', None))

    def test_check_for_selection_dim__no_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__0d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 0)
        with self.assertRaises(AppConfigError):
            obj._check_for_selection_dim(_selection)

    def test_check_for_selection_dim__0d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[42], np.r_[3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 0)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__1d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 1)
        with self.assertRaises(AppConfigError):
            obj._check_for_selection_dim(_selection)

    def test_check_for_selection_dim__1d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[6], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 1)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__2d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[6, 5], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 2)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__6d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3],
                      np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value('result_n_dim', 6)
        with self.assertRaises(AppConfigError):
            obj._check_for_selection_dim(_selection)

    def test_get_single_slice_object__empty_str(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index])

    def test_get_single_slice_object__simple_colon(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', ':')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index])

    def test_get_single_slice_object__sliced(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '1:-1')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 2)

    def test_get_single_slice_object__multiple_single_numbers(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '1, 3, 5, 6, 7')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 5)

    def test_get_single_slice_object__multiple_numbers_w_duplicates(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '1, 3, 5, 1, 5')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 3)

    def test_get_single_slice_object__multiple_slices(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '0:2, 4:6')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 4)

    def test_get_single_slice_object__multiple_slices_and_numbers(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '1:4, 3, 4, 6:8')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 6)

    def test_get_single_slice_object__slic_ew_open_end(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', '1:')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 1)

    def test_get_single_slice_object__slice_w_open_start(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._active_node])
        obj.set_param_value(f'data_slice_{_index}', ':-1')
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 1)

    def test_get_single_slice_object__slice_w_stepping(self):
       self.populate_WorkflowResults()
       _node = 1
       _index = 4
       obj = WorkflowResultsSelector()
       obj.select_active_node(_node)
       obj._npoints = list(RES.shapes[obj._active_node])
       obj.set_param_value(f'data_slice_{_index}', '0:12:2')
       _slice = obj._get_single_slice_object(_index)
       self.assertEqual(_slice.size, 6)

    def test_get_single_slice_object__slice_w_stepping_only(self):
       self.populate_WorkflowResults()
       _node = 1
       _index = 4
       _arrsize = RES.shapes[_node][_index]
       obj = WorkflowResultsSelector()
       obj.select_active_node(_node)
       obj._npoints = list(RES.shapes[obj._active_node])
       obj.set_param_value(f'data_slice_{_index}', '::2')
       _slice = obj._get_single_slice_object(_index)
       self.assertEqual(_slice.size, _arrsize // 2 + _arrsize % 2)

    def test_update_selection__simple(self):
       self.populate_WorkflowResults()
       _node = 1
       obj = WorkflowResultsSelector()
       obj.select_active_node(_node)
       for _index in range(RES.ndims[_node]):
           obj.set_param_value(f'data_slice_{_index}', '1:')
       obj._update_selection()
       _delta = [RES.shapes[_node][_i] - obj._selection[_i].size
                 for _i in range(RES.ndims[_node])]
       self.assertEqual(_delta, [1] * RES.ndims[_node])

    def test_update_selection__with_use_scan_timeline(self):
       self.populate_WorkflowResults()
       _node = 1
       obj = WorkflowResultsSelector()
       obj.set_param_value('use_scan_timeline', True)
       obj.select_active_node(_node)
       for _index in range(RES.ndims[_node] - 2):
           obj.set_param_value(f'data_slice_{_index}', '1:')
       obj._update_selection()
       _delta = [RES.shapes[_node][_i + 2] - obj._selection[_i].size
                 for _i in range(RES.ndims[_node] - 2)]
       self.assertEqual(_delta[1:], [1] * (RES.ndims[_node] - 3))
       self.assertEqual(obj._selection[0].size,
                        self._scan_n[0] * self._scan_n[1] * self._scan_n[2] - 1)

    def test_selection_property(self):
       self.populate_WorkflowResults()
       _node = 1
       obj = WorkflowResultsSelector()
       obj.select_active_node(_node)
       _slices = obj.selection
       self.assertIsInstance(_slices, tuple)
       for _item in _slices:
           self.assertIsInstance(_item, np.ndarray)



if __name__ == '__main__':
    unittest.main()
