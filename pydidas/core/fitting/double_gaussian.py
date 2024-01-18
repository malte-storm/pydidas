# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Module with the DoubleGaussian class for fitting a double Gaussian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DoubleGaussian"]


from typing import Tuple

from .gaussian import Gaussian
from .multi_peak_mixin import MultiPeakMixin


class DoubleGaussian(MultiPeakMixin, Gaussian):
    """
    Class for fitting a double Gaussian function to data.

    The double Gaussian function has the general form

    f(x) = A0 * (2 * pi)**(-0.5) / sigma0 * exp(-(x - mu0)**2 / ( 2 * sigma0**2))
           + A1 * (2 * pi)**(-0.5) / sigma0 * exp(-(x - mu0)**2 / ( 2 * sigma0**2))
           + bg_0 + x * bg_1

    where A0, A1 are the amplitudes, mu0, mu1 are the expectation values, and
    sigma0, sigma1 is the variance. A polinomial background of 0th or 1st order
    can be added by using additional coefficients.
    bg_0 is an optional background offset and bg_1 is the (optional) first order
    term for the background.

    The fit results will be given in form of a tuple c:

    c : tuple
        The tuple with the function parameters.
        c[0] : amplitude 0
        c[1] : sigma 0
        c[2] : expectation value 0
        c[3] : amplitude 1
        c[4] : sigma 1
        c[5] : expectation value 1
        c[6], optional : A background offset.
        c[7], optional : The polynomial coefficient for a first order background.
    """

    name = "Double Gaussian"
    num_peaks = 2
    param_bounds_low = Gaussian.param_bounds_low * num_peaks
    param_bounds_high = Gaussian.param_bounds_high * num_peaks
    param_labels = [
        f"{key}{i}" for i in range(num_peaks) for key in Gaussian.param_labels
    ]

    @staticmethod
    def fwhm(c: Tuple) -> Tuple[float]:
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float, float]
            The function FWHMs for the first an second peak.
        """
        return (2.354820 * c[1], 2.354820 * c[4])

    @staticmethod
    def area(c: Tuple) -> Tuple[float]:
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal to the amplitude term.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float]
            The areas of the two peaks defined through the given parameters c.
        """
        return (c[0], c[3])

    @staticmethod
    def center(c: Tuple[float]) -> Tuple[float]:
        """
        Get the center positions.

        Parameters
        ----------
        c : Tuple[float]
            The fitted parameters.

        Returns
        -------
        Tuple[float]
            The center positions of the peaks.
        """
        return (c[2], c[5])

    @staticmethod
    def amplitude(c: Tuple) -> Tuple[float]:
        """
        Get the amplitude of the peaks from the values of the fitted parameters.

        For a Gaussian function, this corresponds to

        I_peak = A / (sigma * sqrt(2 * Pi))

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float]
            The peaks' amplitude.
        """
        return (0.39894228 * c[0] / c[1], 0.39894228 * c[3] / c[4])
