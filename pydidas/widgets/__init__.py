# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Package with modified widgets required for creating the pydidas graphical user
interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import dialogues
from . import factory
from . import framework
from . import misc
from . import parameter_config
from . import plugin_config_widgets
from . import selection
from . import silx_plot
from . import workflow_edit

__all__.extend(
    [
        "dialogues",
        "factory",
        "framework",
        "misc",
        "parameter_config",
        "plugin_config_widgets",
        "selection",
        "workflow_edit",
        "silx_plot",
    ]
)

# explicitly import items from subpackages into the module:
from .factory import CreateWidgetsMixIn

__all__.extend(["CreateWidgetsMixIn"])

# import __all__ items from modules:
from .file_dialog import *
from .read_only_text_widget import *
from .scroll_area import *
from .utilities import *

# add modules' __all__ items to package's __all__ items and unclutter the
from . import file_dialog

__all__.extend(file_dialog.__all__)
del file_dialog

from . import read_only_text_widget

__all__.extend(read_only_text_widget.__all__)
del read_only_text_widget

from . import scroll_area

__all__.extend(scroll_area.__all__)
del scroll_area

from . import utilities

__all__.extend(utilities.__all__)
del utilities
