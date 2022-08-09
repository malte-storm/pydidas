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
Subpackage with GUI element and managers to access all of pydidas's
functionality from within a graphical user interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import subpackages
from . import frames
from . import managers
from . import mixins
from . import windows

__all__.extend(["frames", "managers", "mixins", "windows"])

# import __all__ items from modules:
from .gui_excepthook_ import *
from .main_window import *


# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import gui_excepthook_

__all__.extend(gui_excepthook_.__all__)
del gui_excepthook_

from . import main_window

__all__.extend(main_window.__all__)
del main_window
