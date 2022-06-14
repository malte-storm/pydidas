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
The experiment package defines singleton classes used for handling global
data about the experiment and scan.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import setup_experiment
from . import setup_scan

__all__.extend(["setup_experiment", "setup_scan"])

# explicitly import the singleton factories from the subpackages
from .setup_experiment import SetupExperiment, SetupExperimentIoMeta
from .setup_scan import SetupScan, SetupScanIoMeta

__all__.extend(
    ["SetupExperiment", "SetupExperimentIoMeta", "SetupScan", "SetupScanIoMeta"]
)
