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
The dataset module includes the Dataset subclasses of numpy.ndarray with additional
embedded metadata.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"

import os
import h5py as h5
import matplotlib.pyplot as plt
import numpy as np

from pydidas.core import Dataset
from pydidas.data_io import import_data

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

def chi_pos_verification(ds):
    '''
    Verification if dataset ds contains 'chi' and 'position' for d-spacing.
    Returns:
        chi_key: The index associated with 'chi'.
        position_key: A tuple where the first element is the index in axis_labels where 'position' descriptor is found, and the second element is the key in the structured string resembling a dict.    
    '''
    if not isinstance(ds, Dataset):
        raise TypeError('Input has to be of type Dataset.')
        
    axis_labels=ds.axis_labels
    
    # Collect indices where 'chi' is found
    chi_indices = [key for key, value in axis_labels.items() if value == 'chi']

    # Check for multiple 'chi'
    if len(chi_indices) > 1:
        raise KeyError('Multiple "chi" found. Check your dataset.')

    # Check for absence of 'chi'
    if not chi_indices:
        raise ValueError('chi is missing. Check your dataset.')

    # Assuming there's exactly one 'chi', get the index
    chi_key = chi_indices[0]

    reverse_axis_labels = dict(zip(axis_labels.values(), axis_labels.keys()))

    # Process to find 'position' in the complex structured string
    position_key = None
    for value, position_index in reverse_axis_labels.items():
        if isinstance(value, str) and 'position' in value:
            parts = value.split(';')
            for part in parts:
                if 'position' in part:
                    # Assume the part is structured as 'key: description'
                    part_key, _ = part.split(':')
                    part_key = int(part_key.strip())  # Convert the key part to integer
                    position_key = (position_index, part_key)
                    break
            if position_key is not None:
                break

    # Check if 'position' is found
    if position_key is None:
        raise ValueError('Key containing "position" is missing. Check your dataset.')

    return (chi_key, position_key)


                break

    # Check if 'position' is found
    if position_key is None:
        raise ValueError('Key containing "position" is missing. Check your dataset.')

    return (chi_key, position_key)


def extract_d_spacing(ds1, pos_key, pos_idx):
    '''
    Extracts d-spacing
    
    Parameters: 
    - ds1 (Dataset): A Dataset object
    - pos_key (int): Key containing 'position' information
    - pos_idx (int): Index containing 'position' information in substring 
    
    '''    
    _slices = []
    for _dim in range(ds1.ndim):
        if _dim != pos_key:
            _slices.append(slice(None, None))
        elif _dim == pos_key:
            _slices.append(slice(pos_idx, pos_idx + 1))
        #print(f"Dimension {_dim}, Slices: {_slices}")
        
    d_spacing = ds1[*_slices]
    d_spacing = d_spacing.squeeze()
        
    return d_spacing


def ds_slicing(ds1):
    '''
    Extracts d-spacing values and associated chi values from a Dataset object for one scan position.

    Parameters:
    - ds1 (Dataset): A Dataset object. 

    Returns:
    - chi (array-like): Array of chi values associated with the extracted d-spacing values.
    - d_spacing (array-like): Array of d-spacing values extracted from the Dataset object.

    Raises:
    - TypeError: If the input is not of type Dataset.
    - ValueError: If the dimension of the d_spacing is not 1.
    '''

    if not isinstance(ds1, Dataset):
        raise TypeError('Input has to be of type Dataset.')
      
    chi_key, (pos_key, pos_idx) = chi_pos_verification(ds1)
    
    #select the chi values
    chi=ds1.axis_ranges[chi_key]
    
    # Extract d-spacing values
    d_spacing = extract_d_spacing(ds1, pos_key, pos_idx)
    
    if d_spacing.size == 0: 
        #Should check for empty arrays in case of slicing beyond bounds
        raise ValueError('Array is empty.')
    
    if not d_spacing.ndim == 1: 
        raise ValueError('Dimension mismatch.')
                       
    return chi, d_spacing

def combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg):
    '''
    Combines the positive and negative slopes of d_spacing and sorts them in ascending order of sin2chi.
    Parameters:
    - d_spacing_pos (Dataset): Dataset of d_spacing values for positive slopes.
    - d_spacing_neg (Dataset): Dataset of d_spacing values for negative slopes.
    Returns:
    - d_spacing_combined (Dataset): Dataset of combined d_spacing values.
    '''
    # Check if the input is of type Dataset
    if not isinstance(d_spacing_pos, Dataset) or not isinstance(d_spacing_neg, Dataset):
        raise TypeError('Input has to be of type Dataset.')
    
    # Check if the axis labels are the same
    if d_spacing_pos.axis_labels != d_spacing_neg.axis_labels:
        raise ValueError('Axis labels do not match.')
    
    
    # Check if the axis ranges are the same, 
    # Create a mask for non-nan values in both arrays
    s2c_axis_pos = d_spacing_pos.axis_ranges[0]
    s2c_axis_neg = d_spacing_neg.axis_ranges[0]
    
    if s2c_axis_pos.shape != s2c_axis_neg.shape:
        raise ValueError("Axis ranges do not have the same length.")
       
    comparison = np.allclose(s2c_axis_pos, s2c_axis_neg, atol=1e-15)   
    if not comparison:
        raise ValueError('Axis ranges do not match.')

    
    # Make copies of the arrays
    s2c_axis_pos_copy = np.copy(s2c_axis_pos)
    d_spacing_pos_copy = np.copy(d_spacing_pos)
    s2c_axis_neg_copy = np.copy(s2c_axis_neg)
    d_spacing_neg_copy = np.copy(d_spacing_neg)
    
    # Get the indices that would sort s2c_mean_pos_copy in ascending order
    sorted_idx_pos = np.argsort(s2c_axis_pos_copy, kind='mergesort')
    sorted_idx_neg = np.argsort(s2c_axis_neg_copy, kind='mergesort')
    
    # Sorting the arrays
    s2c_axis_pos_sorted = s2c_axis_pos_copy[sorted_idx_pos]
    d_spacing_pos_sorted = d_spacing_pos_copy[sorted_idx_pos]
    s2c_axis_neg_sorted = s2c_axis_neg_copy[sorted_idx_neg]
    d_spacing_neg_sorted = d_spacing_neg_copy[sorted_idx_neg]
     
    d_spacing_combi_arr = np.vstack((d_spacing_neg_sorted, d_spacing_pos_sorted))
       
      
    d_spacing_combined = Dataset(d_spacing_combi_arr , 
                                 axis_ranges={0: np.arange(2), 1:  s2c_axis_pos_sorted}, 
                                 axis_labels={0: ['d-', 'd+'], 1: 'sin2chi'})
    
    print(d_spacing_combined.shape)
    print(d_spacing_combined.axis_ranges)
    
    fig, ax =plt.subplots()
    ax.plot(d_spacing_combined.axis_ranges[1], d_spacing_combined.array[0,:], label='d-', linestyle='None', marker='s')
    ax.plot(d_spacing_combined.axis_ranges[1], d_spacing_combined.array[1,:], label='d+',linestyle='None',  marker='o')
    ax.plot(d_spacing_combined.axis_ranges[1], np.nanmean(d_spacing_combined.array[:,:], axis=0), label ="'d+'+'d-'/2", linestyle='None',  marker='x')
    ax.set_ylabel('d [nm]')
    ax.set_xlabel('sin^2(chi)')
    ax.set_title('sin^2(chi) vs d_spacing')
    fig.legend()
    ax.grid()
    fig.show()
    # (d+ +d-)/2 in general np.mean(d+,d-)
    # d(+) - d(-) vs sin(2*chi)  #different graph, linear fit, force through 0
    return d_spacing_combined


def idx_s2c_grouping(chi, tolerance=1e-4):
        
    '''
    Find all chis belonging to the same sin(chi)**2 values within the tolerance value. 
    Parameters:
    - chi (np.ndarray): Array of chi angles in degrees. This should be a 1D numpy array.
    - tolerance (float, optional): The tolerance level for grouping sin^2(chi) values.
        Defaults to 1e-4. This ensures all different groups are caught. 

    Returns:
    - n_components (int): The number of unique groups formed.
    - s2c_labels (np.ndarray): An array of the same shape as chi, where each element
        is an integer label corresponding to the group of its sin^2(chi) value.
        
    Raises:
    - TypeError: If the input `chi` is not a numpy ndarray.
        
    '''
    if not isinstance(chi, np.ndarray):
        raise TypeError('Chi needs to be an np.ndarray.')


    s2c=np.sin(np.deg2rad(chi))**2
    arr=s2c

    # Create the similarity matrix
    similarity_matrix = np.abs(arr - arr[:, np.newaxis]) < tolerance

    # Convert boolean matrix to sparse matrix
    sparse_matrix = csr_matrix(similarity_matrix.astype(int))

    # Find connected components
    n_components, s2c_labels = connected_components(csgraph=sparse_matrix, directed=False, return_labels=True)

    return n_components, s2c_labels

def group_d_spacing_by_chi(d_spacing, chi, tolerance=1e-4):
    '''
    Parameters:
    - chi (np.ndarray): Array of chi angles in degrees. This should be a 1D numpy array.
    - d_spacing (pydidas Dataset): Dataset of d_spacing values. 
    - tolerance (float): The tolerance level for grouping sin^2(chi) values.
    Defaults to 1e-4. This ensures all different groups are caught. 
    '''

    if not isinstance(chi, np.ndarray):
        raise TypeError('Chi has to be of type np.ndarray')
    
    if not isinstance(d_spacing, Dataset):
        raise TypeError('d_spacing has to be of type Pydidas Dataset.')
    
    
    # n_components: number of groups after grouping
    # s2c_lables: sin2chi divided into different groups 
    n_components, s2c_labels = idx_s2c_grouping(chi, tolerance=tolerance)
        
    # Calculate sin2chi
    s2c=np.sin(np.deg2rad(chi))**2
    
    # both are ordered in ascending order of increasing sin2chi
    s2c_unique_labels = np.unique(s2c_labels)
    s2c_unique_values = s2c[s2c_unique_labels]
        
    
    #print('s2c_labels', s2c_labels)
    #print('chi', chi)
    #print('s2c_values', s2c)
    #print('s2c unique labels', np.unique(s2c_labels))
    #print('s2c unique values', s2c[np.unique(s2c_labels)])
    #print('s2c', s2c.shape, s2c)
    
    # Calculate first derivative
    first_derivative = np.gradient(s2c, edge_order=2)
    
    # Define the threshold for being "close to zero", i.e. where is the slope=0
    zero_threshold = 1e-4   
        
    # Categorize the values of the first_derivative
    # 1 is close to zero
    # 2 is positive
    # 0 is negative
    categories = np.zeros_like(first_derivative, dtype=int)
    categories[first_derivative > zero_threshold] = 2
    categories[first_derivative < -zero_threshold] = 0
    categories[(first_derivative >= -zero_threshold) & (first_derivative <= zero_threshold)] = 1
        
    #Filter
    # values close to zero (categories == 1) are added to both sides of the maximum or minimum
    mask_pos = (categories == 2) | (categories == 1 )
    mask_neg = (categories == 0)  | (categories == 1 )
        
    # Advanced indexing 
    # Here, s2c_labels specifies the row indices, and np.arange(s2c_num_elements) specifies the column indices. 
    s2c_advanced_idx = (s2c_labels, np.arange(s2c.size))
    # expected shape for future matrices
    s2c_groups_matrix_shape = s2c_unique_labels.size, s2c.size
    #print('s2c_groups_matrix_shape', s2c_groups_matrix_shape)
    
    # s2c_label_matrix and d_spacing_matrix are useful for quality assurance via visual inspection
    s2c_labels_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    s2c_labels_matrix[*s2c_advanced_idx] = s2c_labels
    #print('s2c_labels_matrix\n', s2c_labels_matrix)
    
    d_spacing_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    d_spacing_matrix[*s2c_advanced_idx] = d_spacing
    
    s2c_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    s2c_matrix[*s2c_advanced_idx] = s2c
    
    # Create pre-filled matrices for filtering based on the slopes and groups
    d_spacing_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
    d_spacing_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan) 
    s2c_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
    s2c_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
        
    # Apply masks to create filtered matrices
    # Combination of advanced indexing and conditional assignment with np.where
    d_spacing_pos_slope_matrix[*s2c_advanced_idx] = np.where(mask_pos, d_spacing, np.nan)
    s2c_pos_slope_matrix[*s2c_advanced_idx] = np.where(mask_pos, s2c, np.nan)

    d_spacing_neg_slope_matrix[*s2c_advanced_idx] = np.where(mask_neg, d_spacing, np.nan)
    s2c_neg_slope_matrix[*s2c_advanced_idx] = np.where(mask_neg, s2c, np.nan)
    

    # Averaging, positive slope
    s2c_mean_pos = np.nanmean(s2c_pos_slope_matrix, axis=1)
    d_spacing_mean_pos = np.nanmean(d_spacing_pos_slope_matrix, axis=1)
    # Averaging, negative slope
    s2c_mean_neg = np.nanmean(s2c_neg_slope_matrix, axis=1)
    d_spacing_mean_neg = np.nanmean(d_spacing_neg_slope_matrix, axis=1)
    # Aim for a complete common s2c_mean_pos/neg without NaN values
    s2c_mean = np.nanmean(np.vstack((s2c_mean_pos, s2c_mean_neg)), axis=0)
    #TODO:
    #The x-axis values are given by 0..max(s2c_labels) because of the way how the matrices are populated.
    #This has also the advantage of automatic sorting in ascending order.
    #Hence, I think s2c_mean = s2c[s2c_unique_labels] is correct
    #print('Comparison of s2c selection:', np.allclose(s2c_mean, s2c[s2c_unique_labels]))
    #If we want s2c[s2c_unique_labels] for the axis_ranges for sin2chi,
    # we don't need to populate the matrixes for s2c_pos_slope_matrix like this
    #If we don't use s2c_mean, sometimes one of the s2c_mean_pos or s2c_mean_neg has np.nan, for example, if chi = [0,90] only.
    # This is due to the fact, that the matrices are prepopulated with np.nan.   
    # A way around is to use s2c_mean=s2c[s2c_unique_labels] and this could reduce code above.
    #print('s2c_mean', s2c_mean) 
    #print( 's2c_mean_pos', s2c_mean_pos)
    #print('s2c_mean_neg', s2c_mean_neg)
    
    
    #create Datasets for output
    #TODO: if wished later to be changed to s2c[s2c_unique_labels] for s2c_mean
    d_spacing_pos=Dataset(d_spacing_mean_pos, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin2chi'} )   
    d_spacing_neg=Dataset(d_spacing_mean_neg, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin2chi'} ) 
    
    return (d_spacing_pos, d_spacing_neg)






