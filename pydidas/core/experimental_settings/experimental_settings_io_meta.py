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
Module with the ExperimentalSettingsIoMeta class which is used for creating
exporter/importer classes for the ExperimentalSetting singleton and
registering them.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettingsIoMeta']


import os

from ..file_extension_registry_metaclass import FileExtensionRegistryMetaclass


class ExperimentalSettingsIoMeta(FileExtensionRegistryMetaclass):
    """
    Metaclass for WorkflowTree exporters and importers which holds the
    registry with all associated file extensions for exporting WorkflowTrees.
    """
    # need to redefine the registry to have a unique registry for
    # ExperimentalSettingsIoMeta
    registry = {}

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Call the concrete export_to_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.
        tree : pydidas.workflow_tree.WorkflowTree
            The instance of the WorkflowTree
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        _extension = os.path.splitext(filename)[1]
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _io_class.export_to_file(filename, **kwargs)

    @classmethod
    def import_from_file(cls, filename):
        """
        Call the concrete import_from_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.

        Returns
        -------
        pydidas.workflow_tree.WorkflowTree
            The new WorkflowTree instance.
        """
        _extension = os.path.splitext(filename)[1]
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _io_class.import_from_file(filename)
