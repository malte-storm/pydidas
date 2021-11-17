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

"""Subpackage with GUI elements."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import io

from . import scan_settings
from .scan_settings import ScanSettings

from . import experimental_settings
from .experimental_settings import ExperimentalSettings

__all__ += ['ExperimentalSettings', 'ScanSettings']


# import modules:

from . import parameter
from .parameter import *

from . import dataset
from .dataset import *

from . import parameter_collection
from .parameter_collection import *

from . import object_with_parameter_collection
from .object_with_parameter_collection import *

from . import composite_image
from .composite_image import *

from . import generic_parameters
from .generic_parameters import *

from . import hdf5_key
from .hdf5_key import *

from . import singleton_factory
from .singleton_factory import *

from . import pydidas_q_settings_mixin
from .pydidas_q_settings_mixin import *

from . import image_metadata_manager
from .image_metadata_manager import *

from . import filelist_manager
from .filelist_manager import *

from . import pydidas_q_settings
from .pydidas_q_settings import *

__all__ += parameter_collection.__all__
__all__ += parameter.__all__
__all__ += object_with_parameter_collection.__all__
__all__ += dataset.__all__
__all__ += hdf5_key.__all__
__all__ += composite_image.__all__
__all__ += generic_parameters.__all__
__all__ += singleton_factory.__all__
__all__ += pydidas_q_settings_mixin.__all__
__all__ += image_metadata_manager.__all__
__all__ += filelist_manager.__all__
__all__ += pydidas_q_settings.__all__


# Unclutter namespace: remove modules from namespace
del parameter
del dataset
del hdf5_key
del parameter_collection
del object_with_parameter_collection
del composite_image
del generic_parameters
del singleton_factory
del pydidas_q_settings_mixin
del image_metadata_manager
del filelist_manager
del pydidas_q_settings
