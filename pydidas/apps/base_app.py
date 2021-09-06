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

"""Module with the BaseApp from which all apps should inherit.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseApp']


from copy import copy

from pydidas.core import ObjectWithParameterCollection


class BaseApp(ObjectWithParameterCollection):
    """
    Inherits from :py:class:`pydidas.core.ObjectWithParameterCollection
    <pydidas.core.ObjectWithParameterCollection>`

    The BaseApp is the base class for all pydidas applications.
    """
    parse_func = None

    def __init__(self, *args, **kwargs):
        """
        Create a Base instance.

        Parameters
        ----------
        *args : list
            Any arguments. Defined by the concrete
            implementation of the app.
        **kwargs : dict
            A dictionary of keyword arguments. Defined by the concrete
            implementation of the app.
        """
        super().__init__()
        self.add_params(*args, **kwargs)
        self._config = {}
        self.slave_mode = kwargs.get('slave_mode', False)
        self.set_default_params()
        self.parse_args_and_set_params()

    def parse_args_and_set_params(self):
        """
        Parse the command line arguments and update the corresponding
        Parameter values.
        """
        if self.parse_func is None:
            return
        _cmdline_args = self.parse_func()
        for _key in self.params:
            if _key in _cmdline_args and _cmdline_args[_key] is not None:
                self.params.set_value(_key, _cmdline_args[_key])

    def run(self):
        """
        Run the app without multiprocessing.
        """
        self.multiprocessing_pre_run()
        tasks = self.multiprocessing_get_tasks()
        for task in tasks:
            self.multiprocessing_pre_cycle(task)
            _carryon = self.multiprocessing_carryon()
            if _carryon:
                _results = self.multiprocessing_func(task)
                self.multiprocessing_store_results(task, _results)
        self.multiprocessing_post_run()

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        raise NotImplementedError

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """
        raise NotImplementedError

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        raise NotImplementedError

    def multiprocessing_pre_cycle(self, *args):
        """
        Perform operations in the pre-cycle of every task.
        """
        return

    def multiprocessing_func(self, *args):
        """
        Perform key operation with parallel processing.
        """
        raise NotImplementedError

    def multiprocessing_carryon(self):
        """
        Wait for specific tasks to give the clear signal.

        This method is called in the parallel multiprocessing process
        prior to the actual calculation. Apps can specify wait conditions
        that need to be fulfilled before carrying on. The method returns
        a boolean flag whether a timeout was encountered.

        Returns
        -------
        carryon : bool
            Flag whether processing can continue or should wait.
        """
        return True

    def get_config(self):
        """
        Get the App configuration.

        Returns
        -------
        dict
            The App configuration stored in the _config dictionary.
        """
        return copy(self._config)

    def copy(self):
        """
        Get a copy of the App.

        Returns
        -------
        App : BaseApp
            A copy of the App instance.
        """
        return copy(self)

    def __copy__(self):
        _obj_copy = type(self)()
        for _key in self.__dict__:
            _obj_copy.__dict__[_key] = copy(self.__dict__[_key])
        return _obj_copy
