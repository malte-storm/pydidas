# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the CompositeImage class used for creating mosaic images."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeImage']

import numpy as np
from pydidas.core.parameter_collection import ParameterCollection
from pydidas.core.object_with_parameter_collection import ParameterCollectionMixIn
from pydidas.core.generic_parameters import get_generic_parameter
from pydidas.core.export_image_func import export_image

class CompositeImage(ParameterCollectionMixIn):
    """
    The CompositeImage class holds a numpy array to insert individual images
    to a composite.
    """
    default_params = ParameterCollection(
        get_generic_parameter('image_shape'),
        get_generic_parameter('composite_nx'),
        get_generic_parameter('composite_ny'),
        get_generic_parameter('composite_dir'),
        get_generic_parameter('datatype'),
        get_generic_parameter('threshold_low'),
        get_generic_parameter('threshold_high'),
        )

    def __init__(self, *args, **kwargs):
        self.params = ParameterCollection(self.default_params.get_copy())
        self.__image = None
        for _key in kwargs:
              self.set_param_value(_key, kwargs[_key])
        if self.__check_config():
            self.__create_image_array()

    def __check_config(self):
        """
        Check whether the config is consistent.

        Returns
        -------
        _okay : bool
            The method returns True if all Parameters have been set correctly.
        """
        _okay = True
        if not self.get_param_value('image_shape')[0] > 0:
            _okay = False
        if not self.get_param_value('image_shape')[1] > 0:
            _okay = False
        if not self.get_param_value('composite_nx') > 0:
            _okay = False
        if not self.get_param_value('composite_ny') > 0:
            _okay = False
        return _okay

    def __verify_config(self):
        """
        Verify all required Parameters have been set.

        Raises
        ------
        ValueError
            If one or more of the required config fields have not been set.

        Returns
        -------
        None.
        """
        if not self.__check_config():
            raise ValueError('Not all required values for the creation of a '
                             'CompositeImage have been set.')

    def __create_image_array(self):
        """
        Create the image array.

        This method creates the array based on the configuration and prepares
        it for inserting images.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.__verify_config()
        _shape = self.get_param_value('image_shape')
        _nx = _shape[1] * self.get_param_value('composite_nx')
        _ny = _shape[0] * self.get_param_value('composite_ny')
        self.__image = np.zeros((_ny, _nx),
                                dtype = self.get_param_value('datatype'))

    def apply_thresholds(self, **kwargs):
        """
        Apply thresholds to the composite image.

        This method applies thresholds to the composite image. By default, it
        will apply the thresholds defined in the ParameterCollection but these
        can be overwritten with the low and high arguments. Note that these
        values will be used to update the ParameterCollection.
        This method will only apply the thresholds to the image but will not
        return the iamge itself.

        Parameters
        ----------
        low : float, optional
            The lower threshold. If not specified, the stored lower threshold
            from the ParameterCollection will be used. By default, that is
            np.nan which will be ignored.
        high : Union[float, None], optional
            The upper threshold. If not specified, the stored upper threshold
            from the ParameterCollection will be used. By default, that is
            np.nan which will be ignored.
        """
        if 'low' in kwargs:
            self.set_param_value('threshold_low', kwargs.get('low'))
        if 'high' in kwargs:
            self.set_param_value('threshold_high', kwargs.get('high'))
        _thresh_low = self.get_param_value('threshold_low')
        if np.isfinite(_thresh_low):
            self.__image[self.__image < _thresh_low] = _thresh_low
        _thresh_high = self.get_param_value('threshold_high')
        if np.isfinite(_thresh_high):
            self.__image[self.__image > _thresh_high] = _thresh_high

    def create_new_image(self):
        """
        Create a new image array with the stored Parameters.

        The new image array is accessible through the .image property.
        """
        self.__create_image_array()

    def insert_image(self, image, index):
        """
        Put the image in the composite image.

        This method will find the correct place for the image in the composite
        and copy the image data there.

        Parameters
        ----------
        image : np.ndarray
            The image data.
        index : int
            The image index. This is needed to find the correct place for
            the image in the composite.

        Returns
        -------
        None.
        """
        if self.__image is None:
            self.__create_image_array()
        if self.get_param_value('composite_dir') == 'x':
            _iy = index // self.get_param_value('composite_nx')
            _ix = index % self.get_param_value('composite_nx')
        else:
            _iy = index % self.get_param_value('composite_ny')
            _ix = index // self.get_param_value('composite_ny')
        yslice = slice(_iy * self.get_param_value('image_shape')[0],
                       (_iy + 1) * self.get_param_value('image_shape')[0])
        xslice = slice(_ix * self.get_param_value('image_shape')[1],
                       (_ix + 1) * self.get_param_value('image_shape')[1])
        self.__image[yslice, xslice] = image

    def save(self, output_fname):
        """
        Save the image in binary npy format.

        Parameters
        ----------
        output_fname : str
            The full filename and path to the output image file.
        """
        np.save(output_fname, self.__image)

    def export(self, output_fname):
        """
        Export the image to a file.

        Parameters
        ----------
        output_fname : str
            The full file system path and filename for the output image file.
        """
        export_image(self.__image, output_fname)

    @property
    def image(self):
        """
        Get the composite image.

        Returns
        -------
        np.ndarray
            The composite image.
        """
        return self.__image

    @property
    def shape(self):
        """
        Get the shape of the composite image.

        Returns
        -------
        tuple
            The shape of the composite image.
        """
        if self.__image is None:
            return (0, 0)
        return self.__image.shape
