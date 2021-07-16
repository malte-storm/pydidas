# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

""" The dataset module includes subclasses of numpy.ndarray with additional
embedded metadata."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Dataset']

import numpy as np


def _default_vals(ndim):
    return {i: None for i in range(ndim)}


class DatasetConfigException(Exception):
    """
    Exception class for Dataset class configuration of metadata.
    """


class EmptyDataset(np.ndarray):
    """
    Inherits from :py:class:`numpy.ndarray`

    Base class of an empty dataset (numpy.ndarray subclass) for instantiation.
    """
    def __new__(cls, *args, **kwargs):
        """
        __new__ method for creation of new numpy.ndarray object.
        """
        local_kws = kwargs.copy()
        for item in ['axis_labels', 'axis_scales', 'axis_units', 'metadata']:
            if item in kwargs:
                del kwargs[item]
        obj = super().__new__(cls, *args, **kwargs)
        obj.axis_labels = local_kws.get('axis_labels', _default_vals(obj.ndim))
        obj.axis_scales = local_kws.get('axis_scales', _default_vals(obj.ndim))
        obj.axis_units = local_kws.get('axis_units', _default_vals(obj.ndim))
        obj.metadata = local_kws.get('metadata', None)
        return obj

    def __array_finalize__(self, obj):
        """
        Finalizazion of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_scales/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None:
            return
        for key in ['axis_labels', 'axis_scales', 'axis_units']:
            _item = getattr(obj, key, _default_vals(self.ndim))
            setattr(self, key,
                    {i: _item.get(i, None) for i in range(self.ndim)})
        self.metadata = getattr(obj, 'metadata', None)

    def __get_dict(self, _data, _text):
        """
        Get an ordered dictionary with the axis keys for _data.

        This method will create a dictionary from lists or tuples and sort
        dictionary keys for dict inputs. The new keys will be 0, 1, ...,
        ndim - 1.

        Parameters
        ----------
        _data : Union[dict, list, tuple]
            The keys for the axis meta data.
        _text : str
            The name of the calling method (for exception handling)

        Raises
        ------
        DatasetConfigException
            If a dictionary is passed as data and the keys do not correspond
            to the set(0, 1, ..., ndim - 1)
        DatasetConfigException
            If a tuple of list is passed and the length of entries is not
            equal to ndim.

        Returns
        -------
        dict
            A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
            values from the input _data.
        """
        if isinstance(_data, dict):
            if set(_data.keys()) != set(np.arange(self.ndim)):
                raise DatasetConfigException(
                    f'The keys for "{_text}" do not match the axis dimensions'
                )
            return  _data #{i: _data[i] for i in range(self.ndim)}
        if isinstance(_data, (list, tuple)):
            _data = dict(zip(np.arange(self.ndim), _data))
            return _data
        raise DatasetConfigException(
            f'Input {_data} cannot be converted to dictionary'
        )

    @property
    def axis_labels(self):
        """
        Get the axis_labels

        Returns
        -------
        dict
            The axis labels: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self.__axis_labels

    @axis_labels.setter
    def axis_labels(self, labels):
        """
        Set the axis_labels metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis labels. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self.__axis_labels = self.__get_dict(labels, 'axis_labels')

    @property
    def axis_scales(self):
        """
        Get the axis scales. These arrays for every dimension give the range
        of the data (in conjunction with the units).

        Returns
        -------
        dict
            The axis scales: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self.__axis_scales

    @axis_scales.setter
    def axis_scales(self, scales):
        """
        Set the axis_scales metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis scales. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self.__axis_scales = self.__get_dict(scales, 'axis_scales')

    @property
    def axis_units(self):
        """
        Get the axis units.

        Returns
        -------
        dict
            The axis units: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self.__axis_units

    @axis_units.setter
    def axis_units(self, units):
        """
        Set the axis_units metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis units. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self.__axis_units = self.__get_dict(units, 'axis_units')

    @property
    def metadata(self):
        """
        Get the image ID.

        Returns
        -------
        integer
            The image ID.
        """
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Set the image metadata.

        Parameters
        ----------
        metadata : Union[dict, None]
            The image metadata.

        Raises
        ------
        ValueError
            If metadata is not None or dict
        """
        if not (isinstance(metadata, dict) or metadata is None):
            raise ValueError('Image id variable is not an integer.')
        self.__metadata = metadata

    @property
    def array(self):
        """
        Get the raw array data of the dataset.

        Returns
        -------
        np.ndarray
            The array data.
        """
        return self.__array__()

    def __repr__(self):
        """
        Reimplementation of the numpy.ndarray.__repr__ method

        Returns
        -------
        str
            The representation of the Dataset class.
        """
        _info = {'axis_labels': self.axis_labels,
                 'axis_scales': self.axis_scales,
                 'axis_units': self.axis_units,
                 'metadata': self.metadata,
                 'array': self.__array__()}
        return (self.__class__.__name__
                + '(\n'
                + ', '.join(f'{i}: {_info[i]}\n' for i in _info)
                + ')')

    def __str__(self):
        """
        Reimplementation of the numpy.ndarray.__str__ method.

        Returns
        -------
        str
            The Dataset.__repr__ string.
        """
        return self.__repr__()


class Dataset(EmptyDataset):
    """
    Inherits from :py:class:`pydidas.core.EmptyDataset
    <pydidas.core.EmptyDataset>`

    Dataset class, a subclass of a numpy ndarray with metadata.

    Parameters for class creation:
    ------------------------------
    array : np.ndarray
        The data array.
    axis_labels : Union[dict, list, tuple], optional
        The labels for the axes. The length must correspond to the array
        dimensions. The default is None.
    axis_scales : Union[dict, list, tuple], optional
        The scales for the axes. The length must correspond to the array
        dimensions. The default is None.
    axis_units : Union[dict, list, tuple], optional
        The units for the axes. The length must correspond to the array
        dimensions. The default is None.
    metadata : Union[dict, None], optional
        A dictionary with metadata. The default is None.
    """
    def __new__(cls, array, *args, **kwargs):
        """
        Create a new Dataset.

        Parameters
        ----------
        array : np.ndarray
            The data array.
        **kwargs : type
            Accepted keywords are axis_labels, axis_scales, axis_units,
            image_id. For information on the keywords please refer to the class
            docstring.

        Returns
        -------
        obj : Dataset
            The new dataset object.
        """
        obj = np.asarray(array).view(cls)
        if 'axis_labels' in kwargs:
            obj.axis_labels = kwargs.get('axis_labels')
        if 'axis_scales' in kwargs:
            obj.axis_scales = kwargs.get('axis_scales')
        if 'axis_units' in kwargs:
            obj.axis_units = kwargs.get('axis_units')
        if 'metadata' in kwargs:
            obj.metadata = kwargs.get('metadata')
        return obj
