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
Module with the FitSinglePeak Plugin which can be used to fit a single peak
in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitSinglePeak"]

import numpy as np
from scipy.optimize import least_squares

from pydidas.core.constants import (
    PROC_PLUGIN,
    gaussian,
    gaussian_delta,
    lorentzian,
    lorentzian_delta,
    voigt,
    voigt_delta,
)
from pydidas.core import (
    get_generic_param_collection,
    Dataset,
    UserConfigError,
    Parameter,
)
from pydidas.core.utils import (
    process_1d_with_multi_input_dims,
    calculate_result_shape_for_multi_input_dims,
)
from pydidas.plugins import ProcPlugin


class FitSinglePeak(ProcPlugin):
    """
    Fit a single peak to a data
    """

    plugin_name = "Fit single peak"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        "process_data_dim",
        "fit_func",
        "fit_bg_order",
        "fit_lower_limit",
        "fit_upper_limit",
    )
    default_params.add_param(
        Parameter(
            "output",
            str,
            "Peak area",
            choices=[
                "Peak area",
                "Peak position",
                "Fit normalized standard deviation",
                "Peak area and position",
                "Peak area, position and norm. std",
            ],
            name="Output",
            tooltip=(
                "The output of the fitting plugin. The plugin can either return"
                " the peak area or the peak position, or both. Alternatively, "
                "The input data, the fitted data and the residual can be returned"
                " as well. Note that the fit parameters are always stored in the "
                "metadata."
            ),
        ),
    )
    input_data_dim = -1
    output_data_dim = 0
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ffunc = None
        self._func = None
        self._data = None
        self._fitparam_labels = []
        self._fitparam_startpoints = []
        self._fitparam_bounds_low = []
        self._fitparam_bounds_high = []

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        self._fitparam_bounds_low = [0, 0, -np.inf]
        self._fitparam_bounds_high = [np.inf, np.inf, np.inf]
        if self.get_param_value("fit_func") == "Gaussian":
            self._func = gaussian
            self._ffunc = gaussian_delta
            self._fitparam_labels = ["amplitude", "sigma", "center"]
        elif self.get_param_value("fit_func") == "Lorentzian":
            self._func = lorentzian
            self._ffunc = lorentzian_delta
            self._fitparam_labels = ["amplitude", "gamma", "center"]
        elif self.get_param_value("fit_func") == "Voigt":
            self._func = voigt
            self._ffunc = voigt_delta
            self._fitparam_labels = ["amplitude", "sigma", "gamma", "center"]
            self._fitparam_bounds_low.insert(1, 0)
            self._fitparam_bounds_high.insert(1, np.inf)
        _bg_order = self.get_param_value("fit_bg_order")
        if _bg_order in [0, 1]:
            self._fitparam_labels.append("background_p0")
            self._fitparam_bounds_low.append(-np.inf)
            self._fitparam_bounds_high.append(np.inf)
        if _bg_order == 1:
            self._fitparam_labels.append("background_p1")
            self._fitparam_bounds_low.append(-np.inf)
            self._fitparam_bounds_high.append(np.inf)
        self.output_data_label = self.get_param_value("output")
        self.output_data_unit = "a.u."
        self._fit_acceptance_threshold = self.q_settings_get_value(
            "global/plugin_fit_std_threshold", dtype=float
        )

    @process_1d_with_multi_input_dims
    def execute(self, data, **kwargs):
        """
        Fit a peak to the data.

        Note that the results includes the original data, the fitted data and
        the residual and that the fit Parameters are included in the kwarg
        metadata.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        self._crop_data_to_selected_range()
        _startguess = self._calc_param_start_guess()
        _res = least_squares(
            self._ffunc,
            _startguess,
            args=(self._x, self._data.array),
            bounds=(self._fitparam_bounds_low, self._fitparam_bounds_high),
        )
        self._fit_params = dict(zip(self._fitparam_labels, _res.x))
        _results = self._create_result_dataset()
        kwargs["fit_params"] = self._fit_params
        kwargs["fit_func"] = self._func.__name__
        return _results, kwargs

    def _crop_data_to_selected_range(self):
        """
        Get the data in the range specified by the limits and store the selected
        x-range and data values.
        """
        _range = self._get_cropped_range()
        if _range.size < 5:
            raise UserConfigError(
                "The data range for the fit is too small with less than 5 data points."
            )
        self._x = self._data.axis_ranges[0][_range]
        self._data = self._data[_range]

    def _get_cropped_range(self):
        """
        Get the cropped index range corresponding to the selected data range.

        Returns
        -------
        range : np.ndarray
            The index range corresponding to the selected data ranges.
        """
        _xlow = self.get_param_value("fit_lower_limit")
        _xhigh = self.get_param_value("fit_upper_limit")
        _range = np.where(
            (self._data.axis_ranges[0] >= _xlow) & (self._data.axis_ranges[0] <= _xhigh)
        )[0]
        return _range

    def _calc_param_start_guess(self):
        """
        Calculate the fit starting Parameters based on the x-range and the data.

        Returns
        -------
        startguess : list
            The list with the starting guess for the

        """
        if self.get_param_value("fit_func") == "Gaussian":
            _startguess = self._get_gaussian_startparams()
        elif self.get_param_value("fit_func") == "Lorentzian":
            _startguess = self._get_lorentzian_startparams()
        elif self.get_param_value("fit_func") == "Voigt":
            _startguess = self._get_voigt_startparams()
        # add the start guess for the center x0:
        _startguess.append(self._x[self._x.size // 2])

        _bg_order = self.get_param_value("fit_bg_order")
        if _bg_order in [0, 1]:
            _startguess.append(np.amin(self._data))
        if _bg_order == 1:
            _startguess.append(0)
        return _startguess

    def _get_gaussian_startparams(self):
        """
        Get the starting parameters for the fit of a Gaussian function to the data.

        Returns
        -------
        list
            A list with entries for the amplitude, sigma.
        """
        # guess that the interval is around twice the FWHM
        _sigma = (self._x[-1] - self._x[0]) / (2 * 2.35)

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is
        # 1 / (sqrt(2 * PI) * sigma) = 1 / (0.40 * sigma)
        _amp = (np.amax(self._data) - np.amin(self._data)) / (0.4 * _sigma)
        return [_amp, _sigma]

    def _get_lorentzian_startparams(self):
        """
        Get the starting parameters for the fit of a Lorentzian function to the data.

        Returns
        -------
        list
            A list with entries for the amplitude, gamma.
        """
        # guess that the interval is around twice the FWHM
        _gamma = (self._x[-1] - self._x[0]) / 4

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is gamma / pi
        _amp = (np.amax(self._data) - np.amin(self._data)) / (_gamma / np.pi)
        return [_amp, _gamma]

    def _get_voigt_startparams(self):
        """
        Get the starting parameters for the fit of a Voigt function to the data.

        Returns
        -------
        list
            A list with entries for the amplitude, sigma, gamma.
        """
        # guess that the interval is around twice the FWHM and that both distributions
        # have the same wweight, i.e. the generic values are divided by 2.
        _sigma = (self._x[-1] - self._x[0]) / (2 * 2.35) / 2
        _gamma = (self._x[-1] - self._x[0]) / 4 / 2

        # estimate the amplitude based on the maximum data height and the
        # amplitude of a function with the average of both distributions
        _amp_norm = ((0.4 * _sigma) + (_gamma / np.pi)) / 2
        _amp = (np.amax(self._data) - np.amin(self._data)) / _amp_norm
        return [_amp, _sigma, _gamma]

    def _create_result_dataset(self):
        """
        Create a new Dataset from the original data and the data fit including
        all the old metadata.

        Note that this method does not upate the new metadata with the fit
        parameters. The new dataset includes a second dimensions with entries
        for the raw data, the data fit and the residual.

        Returns
        -------
        new_data : pydidas.core.Dataset
            The new dataset.
        """
        _output = self.get_param_value("output")
        _datafit = self._func(list(self._fit_params.values()), self._x)
        _residual = self._data - _datafit
        _residual_std = abs(np.std(_residual) / np.mean(self._data))
        if _output == "Peak area":
            _new_data = Dataset(
                [self._fit_params["amplitude"]], axis_labels=["Peak area"]
            )
        elif _output == "Peak position":
            _new_data = Dataset(
                [self._fit_params["center"]], axis_labels=["Peak position"]
            )
        elif _output == "Peak area and position":
            _new_data = Dataset(
                [self._fit_params["amplitude"], self._fit_params["center"]],
                axis_labels=["Peak area and position"],
            )
        elif _output == "Fit normalized standard deviation":
            _new_data = Dataset(
                [_residual_std], axis_labels=["Fit normalized standard deviation"]
            )
        elif _output == "Peak area, position and norm. std":
            _new_data = Dataset(
                [
                    self._fit_params["amplitude"],
                    self._fit_params["center"],
                    _residual_std,
                ],
                axis_labels=["Peak area, position and norm. std"],
            )
        _new_metadata = {
            "fit_func": self._func.__name__,
            "fit_params": self._fit_params,
            "fit_residual_std": _residual_std,
        }
        _new_data.metadata = self._data.metadata | _new_metadata
        _new_data.data_label = _output
        _new_data.data_unit = "a.u."
        if _residual_std >= self._fit_acceptance_threshold or (
            not self._x[0] <= self._fit_params["center"] <= self._x[-1]
        ):
            _new_data[:] = -1
        return _new_data

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        _output = self.get_param_value("output")
        if _output in [
            "Peak area",
            "Peak position",
            "Fit normalized standard deviation",
        ]:
            self._config["result_shape"] = (1,)
        elif _output == "Peak area and position":
            self._config["result_shape"] = (2,)
        elif _output == "Peak area, position and norm. std":
            self._config["result_shape"] = (3,)
        else:
            raise ValueError("No result shape defined for the selected input")

    def get_detailed_results(self):
        """
        Get the detailed results for the background removal.

        This method will return detailed information to display for the user. The return
        format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second, "plot_titles"
        gives a title for each subplot. Third, "plot_ylabels" gives a y axis label for
        each subplot. Fourth, "items" provides  a list with the different items to be
        plotted. Each list entry must be a dictionary with the following keys: "plot"
        [to detemine the plot number], "label" [for the legend label] and "data" with
        the actual data.

        Returns
        -------
        dict
            The dictionary with the detailed results in the format expected by pydidas.
        """
        if self._data is None:
            raise ValueError("Cannot get detailed results without input data.")
        _xfit = np.linspace(self._x[0], self._x[-1], num=(self._x.size - 1) * 10 + 1)
        _datafit = Dataset(
            self._func(list(self._fit_params.values()), _xfit),
            axis_ranges=[_xfit],
            axis_labels=self._data.axis_labels,
            axis_units=self._data.axis_units,
            data_unit=self._data.data_unit,
        )
        _residual = self._data - self._func(list(self._fit_params.values()), self._x)
        _return = {
            "n_plots": 2,
            "plot_titles": {0: "data and fit", 1: "residual"},
            "plot_ylabels": {
                0: "intensity / a.u.",
                1: "intensity / a.u.",
            },
            "items": [
                {"plot": 0, "label": "input data", "data": self._data},
                {"plot": 0, "label": "fitted_data", "data": _datafit},
                {"plot": 1, "label": "residual", "data": _residual},
            ],
        }
        if self.get_param_value("fit_bg_order") is not None:
            _bg_poly = [self._fit_params["background_p0"]]
            if "background_p1" in self._fit_params:
                _bg_poly.insert(0, self._fit_params["background_p1"])
            _bg = Dataset(
                np.polyval(_bg_poly, self._x),
                axis_ranges=[self._x],
                axis_labels=self._data.axis_labels,
                axis_units=self._data.axis_units,
                data_unit=self._data.data_unit,
            )
            _return["items"].append({"plot": 0, "label": "background", "data": _bg})
        return _return
