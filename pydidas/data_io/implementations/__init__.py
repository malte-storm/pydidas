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
The data_io.implementations package includes imports/exporters for data
in different formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .io_base import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import io_base
__all__.extend(io_base.__all__)
del io_base

# Automatically find and import IO classes to have them registered
# with the Metaclass:
import os
import importlib
_dir = os.path.dirname(__file__)
_io_classes = set(item.strip('.py') for item in os.listdir(_dir)
                  if (item.endswith('.py')
                      and item not in ['io_base.py', '__init__.py']))

for _module in _io_classes:
    _module = importlib.import_module(f'.{_module}', __package__)
    __all__ += _module.__all__

del _module
del os
del importlib
