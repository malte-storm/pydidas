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
The apps.parsers subpackage includes parsers to allow running apps on the
command line with command-line calling arguments.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from ._composite_creator_app_parser import *
from ._directory_spy_app_parser import *
from ._execute_workflow_app_parser import *


__all__ = (
    _composite_creator_app_parser.__all__
    + _directory_spy_app_parser.__all__
    + _execute_workflow_app_parser.__all__
)

# Clean up the namespace:
del (
    _composite_creator_app_parser,
    _directory_spy_app_parser,
    _execute_workflow_app_parser,
)
