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
"""
Module with the WorkflowNode class which is a subclasses GenericNode
with additional support for plugins and a plugin chain.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowNode']

from copy import copy
from numbers import Integral
from collections.abc import Iterable

from .generic_node import GenericNode
from ..plugins import BasePlugin


class WorkflowNode(GenericNode):
    """
    The WorkflowNode subclass of the GenericNode has an added plugin attribute
    to allow it to execute plugins, either individually or the full chain.
    """
    def __init__(self, **kwargs):
        self.plugin = None
        super().__init__(**kwargs)
        self.__confirm_plugin_existance_and_type()
        self.plugin.node_id = self._node_id

    def __confirm_plugin_existance_and_type(self):
        """
        Verify that a plugin exists and is of the correct type.

        Raises
        ------
        KeyError
            If no plugin has been selected.
        TypeError
            If the plugin is not an instance of BasePlugin.
        """
        if self.plugin is None:
            raise KeyError('No plugin has been supplied for the WorkflowNode.'
                           ' Node has not been created.')
        if not isinstance(self.plugin, BasePlugin):
            raise TypeError('Plugin must be an instance of BasePlugin (or '
                            'subclass).')

    def prepare_execution(self):
        """
        Prepare the execution of the plugin chain by calling the pre_execute
        methods of all plugins.
        """
        self.plugin.pre_execute()
        for _child in self._children:
            _child.prepare_execution()

    def execute_plugin(self, *args, **kwargs):
        """
        Execute the plugin associated with the node.

        Parameters
        ----------
        *args : tuple
            Any arguments which need to be passed to the plugin.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin.

        Returns
        -------
        results : tuple
            The result of the plugin.execute method.
        kws : dict
            Any keywords required for calling the next plugin.
        """
        return self.plugin.execute(*args, **kwargs)

    def execute_plugin_chain(self, arg, **kwargs):
        """
        Execute the full plugin chain recursively.

        This method will call the plugin.execute method and pass the results
        to the node's children and call their execute_plugin_chain methods.
        Note: No result callback is intended. It is assumed that plugin chains
        are responsible for saving their own data at the end of the processing.

        Parameters
        ----------
        *args : tuple
            Any arguments which need to be passed to the plugin.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin.
        """
        res, reskws = self.plugin.execute(copy(arg), **copy(kwargs))
        for _child in self._children:
            _child.execute_plugin_chain(res, **reskws)
        if self.is_leaf:
            self.results = res
            self.result_kws = reskws
