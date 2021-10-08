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

"""The composites module includes the Composite class for handling composite image data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResults']

import multiprocessing
import numpy as np

from ..core.singleton_factory import SingletonFactory
from ..core.scan_settings import ScanSettings
from .workflow_tree import WorkflowTree

SCAN = ScanSettings()

TREE = WorkflowTree()


class _WorkflowResults:
    """
    WorkflowResults is a class for handling composite data which spans
    individual images.
    """

    def __init__(self):
        self.__composites = {}

    def update_shapes_from_scan(self):
        """
        Update the shape of the results from the ScanSettings.
        """
        _dim = SCAN.get_param_value('scan_dim')
        _points = tuple([SCAN.get_param_value(f'n_points_{_n}')
                         for _n in range(1, _dim + 1)])
        _results = TREE.get_all_result_shapes()
        _shapes = {_key: _points + _shape for _key, _shape in _results.items()}
        for _node_id, _shape in _shapes.items():
            self.__composites[_node_id] = np.zeros(_shape, dtype=np.float32)

    def store_results(self, index, results_dict):
        _scan_index = SCAN.get_frame_position_in_scan(index)
        for _key, _val in results_dict.items():
            self.__composites[_key][_scan_index] = _val



WorkflowResults = SingletonFactory(_WorkflowResults)
