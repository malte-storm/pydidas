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

""" The dataset module includes subclasses of numpy.ndarray with additional
embedded metadata."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Dataset']

from numbers import Integral
from collections.abc import Iterable
from copy import copy

import numpy as np

from pydidas._exceptions import DatasetConfigException


def _default_vals(ndim):
    """
    Generate default values of None for a number of dimensions.

    Parameters
    ----------
    ndim : int
        The number of dimensions

    Returns
    -------
    dict
        A dict with entries of type (dim: None).
    """
    return {i: None for i in range(ndim)}


def _insert_axis_key(original_dict, dim):
    """
    Insert a new axis key at the specified dimension.

    Parameters
    ----------
    original_dict : dict
        The original dictionary.
    dim : int
        The dimension in front of which the new key shall be inserted.

    Returns
    -------
    dict
        The updated dict with a new key and the other (higher-dim)
        keys shifted by one.
    """
    _copy = {}
    for _key in sorted(original_dict):
        if _key < dim:
            _copy[_key] = original_dict[_key]
        elif _key == dim:
            _copy[_key] = None
            _copy[_key + 1] = original_dict[_key]
        else:
            _copy[_key + 1] = original_dict[_key]
    return _copy


class EmptyDataset(np.ndarray):
    """
    Inherits from :py:class:`numpy.ndarray`

    Base class of an empty dataset (numpy.ndarray subclass) for instantiation.
    """

    __safe_for_unpickling__ = True

    def __new__(cls, *args, **kwargs):
        """
        __new__ method for creation of new numpy.ndarray object.
        """
        local_kws = kwargs.copy()
        for item in ['axis_labels', 'axis_ranges', 'axis_units', 'metadata']:
            if item in kwargs:
                del kwargs[item]
        obj = np.ndarray.__new__(cls, *args, **kwargs)
        for key in ['axis_labels', 'axis_ranges', 'axis_units']:
            _data = local_kws.get(key, _default_vals(obj.ndim))
            _labels = obj.__get_dict(_data, '__new__')
            setattr(obj, key, _labels)
        obj.metadata = local_kws.get('metadata', None)
        return obj


    def __array_finalize__(self, obj):
        """
        Finalizazion of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_scales/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None or self.shape == tuple():
            return
        for _att in ['_axis_labels', '_axis_units', '_axis_ranges']:
            if not hasattr(self, _att):
                setattr(self, _att, _default_vals(self.ndim))
        self.metadata = getattr(obj, 'metadata', None)
        self._getitem_key = getattr(obj, '_getitem_key', None)
        _keys = {_key: copy(getattr(obj, _key, _default_vals(self.ndim)))
                 for _key in ['axis_labels', 'axis_ranges', 'axis_units']}
        if self._getitem_key is not None:
            self.__modify_axis_keys(_keys)
        self.__update_keys_for_flattened_array(_keys)
        for _key in ['axis_labels', 'axis_ranges', 'axis_units']:
            setattr(self, _key, list(_keys[_key].values()))
        self._getitem_key = None
        if isinstance(obj, EmptyDataset):
            obj._getitem_key = None

    def __modify_axis_keys(self, keys):
        """
        Modify the axis keys (axis_labels, -_units, and -_ranges) and store
        the new values in place.

        Parameters
        ----------
        keys : dict
            A dictionary with the axis keys.
        """
        if (isinstance(self._getitem_key, np.ndarray)
                and self._getitem_key.ndim > 1):
            return
        for _dim, _cutter in enumerate(self._getitem_key):
            if isinstance(_cutter, Integral):
                for _item in ['axis_labels', 'axis_units', 'axis_ranges']:
                    del keys[_item][_dim]
            elif isinstance(_cutter, (slice, Iterable)):
                if keys['axis_ranges'][_dim] is not None:
                    keys['axis_ranges'][_dim] = (
                        keys['axis_ranges'][_dim][_cutter])
            elif _cutter is None:
                for _item in ['axis_labels', 'axis_units', 'axis_ranges']:
                    keys[_item] = _insert_axis_key(keys[_item], _dim)

    def __update_keys_for_flattened_array(self, keys):
        """
        Update the keys for flattened arrays.

        Parameters
        ----------
        keys : dict
            A dictionary with the axis keys.
        """
        if self.ndim == 1 and (len(keys['axis_ranges']) > 1
                               or len(keys['axis_units']) > 1
                               or len(keys['axis_labels']) > 1):
            keys['axis_labels'] = {0: 'flattened'}
            keys['axis_ranges'] = {0: None}
            keys['axis_units'] = {0: None}

    def flatten(self):
        """
        Clear the metadata when flattening the array.
        """
        self._axis_labels = {0: None}
        self._axis_ranges = {0: None}
        self._axis_units = {0: None}
        return super().flatten()

    def __getitem__(self, key):
        """
        Overwrite the generic __getitem__ method to catch the the slicing
        keys.

        Parameters
        ----------
        key : Union[int, tuple]
            The slicing objects

        Returns
        -------
        pydidas.core.Dataset
            The sliced new dataset.
        """
        self._getitem_key = (key,) if isinstance(key, (int, slice)) else key
        _new = super().__getitem__(key)
        # self._getitem_key = None
        return _new

    def __get_dict(self, _data, method_name):
        """
        Get an ordered dictionary with the axis keys for _data.

        This method will create a dictionary from lists or tuples and sort
        dictionary keys for dict inputs. The new keys will be 0, 1, ...,
        ndim - 1.

        Parameters
        ----------
        _data : Union[dict, list, tuple]
            The keys for the axis meta data.
        method_name : str
            The name of the calling method (for exception handling)

        Raises
        ------
        DatasetConfigException
            If a dictionary is passed as data and the keys do not correspond
            to the set(0, 1, ..., ndim - 1)
        DatasetConfigException
            If a tuple of list is passed and the length of entries is not
            equal to ndim.
○
        Returns
        -------
        dict
            A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
            values from the input _data.
        """
        if isinstance(_data, dict):
            if set(_data.keys()) != set(np.arange(self.ndim)):
                raise DatasetConfigException(
                    f'The keys for "{method_name}" do not match the axis '
                    'dimensions')
            return  _data
        if isinstance(_data, (list, tuple)):
            if len(_data) != self.ndim:
                raise DatasetConfigException(
                    f'The number of entries for "{method_name}" does'
                    ' not match the axis dimensions')
            _data = {index: item for index, item in enumerate(_data)}
            return _data
        raise DatasetConfigException(
            f'Input {_data} cannot be converted to dictionary')

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
        return self._axis_labels

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
        self._axis_labels = self.__get_dict(labels, 'axis_labels')

    @property
    def axis_ranges(self):
        """
        Get the axis ranges. These arrays for every dimension give the range
        of the data (in conjunction with the units).

        Returns
        -------
        dict
            The axis scales: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self._axis_ranges

    @axis_ranges.setter
    def axis_ranges(self, scales):
        """
        Set the axis_ranges metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis scales. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self._axis_ranges = self.__get_dict(scales, 'axis_ranges')

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
        return self._axis_units

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
        self._axis_units = self.__get_dict(units, 'axis_units')

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
            raise TypeError('Metadata must be a dictionary or None.')
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
                 'axis_ranges': self.axis_ranges,
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

    def __reduce__(self):
        """
        Reimplementation of the numpy.ndarray.__reduce__ method to add
        the Dataset metadata to the pickled version.

        This method will add the cls.__dict__ items to the generic
        numpy.ndarray__reduce__ results to pass and store the Dataset axis
        items and metadata.

        Returns
        -------
        tuple
            The arguments required for pickling. Please refer to
            https://docs.python.org/2/library/pickle.html#object.__reduce__
            for the full documentation. The class' state is appended with
            the class' __dict__
        """
        _ndarray_reduced = np.ndarray.__reduce__(self)
        _dataset_state = _ndarray_reduced[2] + (self.__dict__,)
        return (_ndarray_reduced[0], _ndarray_reduced[1], _dataset_state)

    def __setstate__(self, state):
        """
        Reimplementation of the numpy.ndarray.__setstate__.

        This method is called after pickling to restore the object. The
        Dataset's __setstate__ method adds the restoration of the __dict__
        to the generic numpy.ndarray.__setstate__.

        Parameters
        ----------
        state : tuple
            The pickled objcts state.
        """
        self.__dict__ = state[-1]
        np.ndarray.__setstate__(self, state[0:-1])


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
    axis_ranges : Union[dict, list, tuple], optional
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
            Accepted keywords are axis_labels, axis_ranges, axis_units,
            metadata. For information on the keywords please refer to the
            class docstring.

        Returns
        -------
        obj : Dataset
            The new dataset object.
        """
        obj = np.asarray(array).view(cls)
        obj.axis_units = kwargs.get('axis_units', _default_vals(obj.ndim))
        obj.axis_labels = kwargs.get('axis_labels', _default_vals(obj.ndim))
        obj.axis_ranges = kwargs.get('axis_ranges', _default_vals(obj.ndim))
        obj.metadata = kwargs.get('metadata', None)
        return obj
