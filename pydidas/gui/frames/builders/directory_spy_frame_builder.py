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
Module with the DirectorySpyFrameBuilder class which is used to
populate the DirectorySpyFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DirectorySpyFrameBuilder"]

from silx.gui.plot import Plot2D

from ....core.constants import (
    CONFIG_WIDGET_WIDTH,
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    FIX_EXP_POLICY,
    EXP_EXP_POLICY,
)
from ....widgets import ScrollArea, BaseFrameWithApp
from ....widgets.parameter_config import ParameterEditFrame


class DirectorySpyFrameBuilder(BaseFrameWithApp):
    """
    Mix-in class which includes the build_frame method to populate the
    base class's UI and initialize all widgets.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrameWithApp.__init__(self, parent, **kwargs)

    def __param_widget_config(self, param_key):
        """
        Get Formatting options for create_param_widget calls.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.

        Returns
        -------
        dict :
            The dictionary with the formatting options.
        """
        if param_key in [
            "filename_pattern",
            "directory_path",
            "bg_file",
            "hdf5_key",
            "bg_hdf5_key",
        ]:
            _dict = DEFAULT_TWO_LINE_PARAM_CONFIG.copy()
            _dict.update(
                {
                    "parent_widget": self._widgets["config"],
                    "row": self._widgets["config"].next_row(),
                }
            )
        else:
            _dict = dict(
                parent_widget=self._widgets["config"],
                width_io=100,
                width_unit=0,
                width_text=CONFIG_WIDGET_WIDTH - 100,
                width_total=CONFIG_WIDGET_WIDTH,
                row=self._widgets["config"].next_row(),
            )
        if param_key in [
            "directory_path",
            "hdf5_key",
            "bg_file",
            "bg_hdf5_key",
            "bg_hdf5_frame",
        ]:
            _dict["visible"] = False
        return _dict

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "title", "Directory spy", fontsize=14, bold=True, gridPos=(0, 0, 1, 5)
        )

        self.create_spacer("title_spacer", height=20, gridPos=(1, 0, 1, 1))

        self._widgets["config"] = ParameterEditFrame(
            parent=None, init_layout=True, lineWidth=5, sizePolicy=FIX_EXP_POLICY
        )

        self.create_spacer(
            "spacer1", gridPos=(-1, 0, 1, 2), parent_widget=self._widgets["config"]
        )

        self.create_any_widget(
            "config_area",
            ScrollArea,
            widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH + 40,
            sizePolicy=FIX_EXP_POLICY,
            gridPos=(-1, 0, 1, 1),
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )

        for _param in [
            "scan_for_all",
            "filename_pattern",
            "directory_path",
            "hdf5_key",
            "use_global_det_mask",
            "use_bg_file",
            "bg_file",
            "bg_hdf5_key",
            "bg_hdf5_frame",
        ]:
            self.create_param_widget(
                self.get_param(_param), **self.__param_widget_config(_param)
            )

        self.create_line(
            "line_buttons", gridPos=(-1, 0, 1, 1), parent_widget=self._widgets["config"]
        )

        self.create_button(
            "but_once",
            "Show latest image",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
        )

        self.create_button(
            "but_show",
            "Force plot update",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
        )

        self.create_button(
            "but_exec",
            "Start scanning",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
        )

        self.create_button(
            "but_stop",
            "Stop scanning",
            gridPos=(-1, 0, 1, 1),
            enabled=False,
            visible=True,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
        )

        self.create_spacer(
            "config_terminal_spacer",
            height=20,
            gridPos=(-1, 0, 1, 1),
            parent_widget=self._widgets["config"],
        )

        self.create_spacer("menu_bottom_spacer", height=20, gridPos=(-1, 0, 1, 1))

        self.add_any_widget(
            "plot",
            Plot2D(),
            alignment=None,
            gridPos=(0, 1, 3, 1),
            visible=True,
            stretch=(1, 1),
            sizePolicy=EXP_EXP_POLICY,
        )