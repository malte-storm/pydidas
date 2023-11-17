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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ViewResultsFrame"]


from typing import Self

from qtpy import QtCore

from ...contexts.diffraction_exp_context import DiffractionExperiment
from ...contexts.scan_context import Scan
from ...core import get_generic_param_collection
from ...widgets import PydidasFileDialog
from ...widgets.framework import BaseFrame
from ...workflow import ProcessingTree, WorkflowResults, result_io
from ..mixins import ViewResultsMixin
from .builders.view_results_frame_builder import ViewResultsFrameBuilder


SAVER = result_io.WorkflowResultIoMeta


class ViewResultsFrame(BaseFrame, ViewResultsMixin):
    """
    The ViewResultsFrame is used to import and visualize the pydidas WorkflowResults.
    """

    menu_icon = "qta::mdi.monitor-eye"
    menu_title = "Import and display workflow results"
    menu_entry = "Workflow processing/View workflow results"

    default_params = get_generic_param_collection(
        "selected_results", "saving_format", "enable_overwrite"
    )
    params_not_to_restore = ["selected_results"]

    def __init__(self, **kwargs: dict) -> Self:
        self._SCAN = Scan()
        self._TREE = ProcessingTree()
        self._EXP = DiffractionExperiment()
        self._RESULTS = WorkflowResults(
            diffraction_exp_context=self._EXP,
            scan_context=self._SCAN,
            workflow_tree=self._TREE,
        )
        BaseFrame.__init__(self, **kwargs)
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog(
            caption="Workflow results directory",
            dialog_type="open_directory",
            parent=self,
            qsettings_ref="WorkflowResults__import",
        )

    def build_frame(self):
        """
        Build the frame and polulate it with widgets.
        """
        ViewResultsFrameBuilder.build_frame(self)

    def finalize_ui(self):
        """
        Connect the export functions to the results widget data.
        """
        ViewResultsMixin.__init__(self, workflow_results=self._RESULTS)

    def connect_signals(self):
        self._widgets["but_load"].clicked.connect(self.import_data_to_workflow_results)
        self._widgets["plot"].sig_get_more_info_for_data.connect(
            self._widgets["result_selector"].show_info_popup
        )

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        BaseFrame.frame_activated(self, index)
        self._config["frame_active"] = index == self.frame_index

    def import_data_to_workflow_results(self):
        """
        Import data to the workflow results.
        """
        _dir = self.__import_dialog.get_user_response()
        if _dir is not None:
            self._RESULTS.import_data_from_directory(_dir)
            self._RESULTS._TREE.root.plugin._SCAN = self._RESULTS._SCAN
            self._RESULTS._TREE.root.plugin.update_filename_string()
            self.update_choices_of_selected_results()
            self.update_export_button_activation()
