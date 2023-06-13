# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the Lorentzian class for fitting a Lorentzian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Lorentzian"]


from typing import List, Tuple, Union

from numpy import amax, amin, inf, ndarray, pi

from .fit_func_base import FitFuncBase


class Lorentzian(FitFuncBase):
    """
    Class for fitting a Lorentzian function.
    """

    name = "Lorentzian"
    param_bounds_low = [0, 0, -inf]
    param_bounds_high = [inf, inf, inf]
    param_labels = ["amplitude", "gamma", "center"]

    @staticmethod
    def func(c: Tuple[float], x: ndarray) -> ndarray:
        """
        Get the function values for a Lorentzian defined by the parameters c.

        The Lorentzian function has the general form

        L(x) = A / pi * (Gamma / 2) / ((x - x0)**2 + (Gamma / 2)**2 ) + bg_0 + x * bg_1,

        where A is the amplitude, Gamma is the FWHM, x0 is the center. bg_0 is an
        optional background offset and bg_1 is the (optional) first order term for the
        background.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.
            c[0] : amplitude
            c[1] : Gamma
            c[2] : center
        x : ndarray
            The input x data points.

        Returns
        -------
        ndarray
            The Lorentzian function values for the input parameters.
        """
        return c[0] / pi * (0.5 * c[1]) / ((x - c[2]) ** 2 + (0.5 * c[1]) ** 2)

    @classmethod
    def guess_peak_start_params(
        cls, x: ndarray, y: ndarray, index: Union[None, int], **kwargs: dict
    ) -> List[float]:
        """
        Guess the starting parameters for a Lorentzian peak fit.

        Parameters
        ----------
        x : np.ndarray
            The x data points.
        y : np.ndarray
            The function data points to be fitted.
        index : Union[None, str]
            The peak index. Use None for a non-indexed single peak or the integer peak
            number (starting with 1).
        **kwargs : dict
            Optional keyword arguments.

        Returns
        -------
        List[float]
            The list with estimated amplitude, width and center parameters.
        """
        if amin(y) < 0:
            y = y + max(amin(y), -0.2 * amax(y))
            y[y < 0] = 0
        index = "" if index is None else str(index)
        _center_start = kwargs.get(f"center{index}_start", x[y.argmax()])
        _ycenter = cls.get_y_value(_center_start, x, y)

        _high_x = cls.get_fwhm_indices(_center_start, _ycenter, x, y)
        _gamma_start = kwargs.get(f"width{index}_start", None)
        if _gamma_start is None:
            if _high_x.size > 0:
                _gamma_start = (x[_high_x[-1]] - x[_high_x[0]]) / 2
            else:
                _gamma_start = (x[-1] - x[0]) / 5

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is 2 / (pi * Gamma).
        # Because the FWHM is often underestimated, ignore the factor 2
        _amp = (_ycenter - amin(y)) * _gamma_start * pi
        return [_amp, _gamma_start, _center_start]

    @classmethod
    def fwhm(cls, c):
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function FWHM.
        """
        return c[1]

    @staticmethod
    def amplitude(c: Tuple) -> float:
        """
        Get the amplitude of the peak from the values of the fitted parameters.

        For a Lorentzian function, this corresponds to

        I_peak = A / (sigma * sqrt(2 * Pi))

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function amplitude.
        """
        return 2 * c[0] / pi / c[1]
