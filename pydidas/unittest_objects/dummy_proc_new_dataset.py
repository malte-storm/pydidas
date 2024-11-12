# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
The dummy_proc module includes the DummyProc class which can be used to
test workflows and Plugins without any file system operations.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DummyProcNewDataset"]


import numpy as np

# because these Plugins will be loaded directly by importlib, absolute imports
# are required:
from pydidas.core import Dataset, Parameter, ParameterCollection
from pydidas.plugins import ProcPlugin


class DummyProcNewDataset(ProcPlugin):
    """
    A dummy processing plugin which applies a random offset to the input data.
    """

    plugin_name = "Dummy processing Plugin with new Dataset"
    default_params = ParameterCollection(
        Parameter(
            "_output_shape",
            tuple,
            (1,),
            dtype=tuple,
            subtype=int,
            tooltip="The shape of the output data.",
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pre_executed = False
        self._executed = False
        self.set_param_value("_output_shape", kwargs.get("output_shape", (1,)))

    def __reduce__(self):
        """
        Reduce the DummyProcNewDataset for Pickling.

        Returns
        -------
        dummy_getter : callable
            The callable function to create a new instance.
        tuple
            The arguments for plugin_getter. This is only the class name.
        dict
            The state to set the state of the new object.
        """
        from .dummy_getter_ import dummy_getter

        return (dummy_getter, (self.__class__.__name__,), self.__getstate__())

    def execute(self, data: np.ndarray, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Execute the actual computations.

        This method will apply an offset to the image data and store it in the
        kwargs. If the offset is not defined using the "offset" keyword
        argument, a random offset is applied.

        Parameters
        ----------
        data : np.ndarray
            The input data
        **kwargs : dict
            Any keyword arguments

        Returns
        -------
        data: np.ndarray
            The updated data
        kwargs : dict
            The update input kwargs. This method will add the offset to the
            dict keys for reference.
        """
        self._executed = True
        _data = Dataset(np.zeros(self.get_param_value("_output_shape")) + np.mean(data))
        return _data, kwargs

    def pre_execute(self):
        """
        Run the pre-execution routine and store a variable that this method
        has been called.
        """
        self._pre_executed = True

    def calculate_result_shape(self):
        """
        Set the result shape based on the given output_shapae.
        """
        self._config["result_shape"] = self.get_param_value("_output_shape")
