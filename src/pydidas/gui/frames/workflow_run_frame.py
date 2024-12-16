# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the WorkflowRunFrame which allows to run the full
processing workflow and visualize the results.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowRunFrame"]


import time

from qtpy import QtCore, QtWidgets

from pydidas.apps import ExecuteWorkflowApp
from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.utils import ShowBusyMouse, pydidas_logger
from pydidas.gui.frames.builders import WorkflowRunFrameBuilder
from pydidas.gui.mixins import ViewResultsMixin
from pydidas.multiprocessing import AppRunner
from pydidas.widgets.dialogues import WarningBox
from pydidas.widgets.framework import BaseFrameWithApp
from pydidas.workflow import WorkflowTree


TREE = WorkflowTree()
logger = pydidas_logger()


class WorkflowRunFrame(BaseFrameWithApp, ViewResultsMixin):
    """
    A widget for running the ExecuteWorkflowApp and visualizing the results.
    """

    menu_icon = "pydidas::frame_icon_workflow_run"
    menu_title = "Run full workflow"
    menu_entry = "Workflow processing/Run full workflow"

    default_params = get_generic_param_collection(
        "selected_results", "saving_format", "enable_overwrite"
    )
    params_not_to_restore = ["selected_results"]
    sig_processing_running = QtCore.Signal(bool)

    def __init__(self, **kwargs: dict):
        BaseFrameWithApp.__init__(self, **kwargs)
        _global_plot_update_time = self.q_settings_get(
            "global/plot_update_time", dtype=float
        )
        self._config.update(
            {
                "data_use_timeline": False,
                "plot_last_update": 0,
                "plot_update_time": _global_plot_update_time,
            }
        )
        self._axlabels = lambda i: ""
        self._app = ExecuteWorkflowApp()
        self.set_default_params()
        self.add_params(self._app.params)

    def build_frame(self):
        """
        Populate the frame with widgets.
        """
        WorkflowRunFrameBuilder.build_frame(self)

    def connect_signals(self):
        """
        Connect all required Qt slots and signals.
        """
        self.param_widgets["autosave_results"].io_edited.connect(
            self.__update_autosave_widget_visibility
        )
        self._widgets["but_exec"].clicked.connect(self.__execute)
        self._widgets["but_abort"].clicked.connect(self.__abort_execution)
        self._widgets["plot"].sig_get_more_info_for_data.connect(
            self._widgets["result_selector"].show_info_popup
        )

    def finalize_ui(self):
        """
        Connect the export functions to the widget data.
        """
        ViewResultsMixin.__init__(self)

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
        super().frame_activated(index)
        if index == self.frame_index:
            self.update_choices_of_selected_results()
            self.update_export_button_activation()
        self._config["frame_active"] = index == self.frame_index

    def __abort_execution(self):
        """
        Abort the execution of the AppRunner.
        """
        self._widgets["but_abort"].setEnabled(False)
        if self._runner is not None:
            with ShowBusyMouse():
                logger.debug("WorkflowRunFrame: Sending stop signal")
                self._runner.requestInterruption()
                _t0 = time.time()
                while self._runner is not None:
                    if time.time() - _t0 > 5:
                        raise UserConfigError(
                            "Timeout while waiting for AppRunner to abort workflow "
                            "execution. Please consider restarting pydidas before "
                            "processing a workflow again."
                        )
                        break
                    time.sleep(0.02)
                    QtWidgets.QApplication.instance().processEvents()
        self.set_status("Aborted processing of full workflow.")

    @QtCore.Slot()
    def __execute(self):
        """
        Execute the Application in the chosen type (GUI or command line).
        """
        logger.debug("WorkflowRunFrame: Clicked execute")
        self._verify_result_shapes_uptodate()
        self.sig_processing_running.emit(True)
        try:
            self._run_app()
        except:
            self.sig_processing_running.emit(False)
            raise

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        if not self._check_tree_is_populated():
            self.sig_processing_running.emit(False)
            return
        logger.debug("WorkflowRunFrame: Starting workflow")
        self._prepare_app_run()
        self._app.multiprocessing_pre_run()
        self._config["last_update"] = time.time()
        self.__set_proc_widget_visibility_for_running(True)
        logger.debug("WorkflowRunFrame: Starting AppRunner")
        self._runner = AppRunner(self._app)
        self._runner.sig_progress.connect(self._apprunner_update_progress)
        self._runner.sig_results.connect(self.__update_result_node_information)
        self._runner.sig_results.connect(self.__check_for_plot_update)
        self._runner.finished.connect(self._apprunner_finished)
        self._runner.sig_final_app_state.connect(self._set_app)
        self._runner.sig_message_from_worker.connect(self.__process_messages)
        QtWidgets.QApplication.instance().aboutToQuit.connect(
            self._runner.send_stop_signal
        )
        self._config["update_node_information_connected"] = True
        logger.debug("WorkflowRunFrame: Running AppRunner")
        self._runner.start()

    @staticmethod
    def _check_tree_is_populated() -> bool:
        """
        Check if the WorkflowTree is populated, i.e. not empty.

        Returns
        -------
        bool
            Flag whether the WorkflowTree is populated.
        """
        if TREE.root is None:
            WarningBox(
                "Empty WorkflowTree",
                "The WorkflowTree is empty. Workflow processing has not been started.",
            )
            return False
        return True

    def _prepare_app_run(self):
        """
        Do preparations for running the ExecuteWorkflowApp.

        This methods sets the required attributes both for serial and
        parallel running of the app.
        """
        self.set_status("Started processing of full workflow.")
        self._widgets["progress"].setValue(0)
        self._clear_selected_results_entries()
        self._clear_plot()

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        logger.debug("WorkflowRunFrame: Handle AppRunner loop finished signal.")
        self._runner.sig_final_app_state.disconnect()
        self._runner.sig_progress.disconnect()
        self._runner.sig_results.disconnect()
        self._runner.sig_post_run_called.disconnect()
        self._runner.sig_message_from_worker.disconnect()
        self._runner.deleteLater()
        self._runner = None
        logger.debug("WorkflowRunFrame: AppRunner successfully shut down.")
        self.set_status("WorkflowRunFrame: Finished processing of full workflow.")
        self._finish_processing()
        self.update_plot()

    @QtCore.Slot()
    def __update_result_node_information(self):
        """
        Update the information about the nodes' results after the AppRunner
        has sent the first results.
        """
        self._widgets["result_selector"].get_and_store_result_node_labels()
        if self._config["update_node_information_connected"]:
            self._runner.sig_results.disconnect(self.__update_result_node_information)
            self._config["update_node_information_connected"] = False

    @QtCore.Slot()
    def __check_for_plot_update(self):
        _dt = time.time() - self._config["plot_last_update"]
        if _dt > self._config["plot_update_time"] and self._config["frame_active"]:
            self._config["plot_last_update"] = time.time()
            self.update_plot()

    @QtCore.Slot(str)
    def __process_messages(self, message: str):
        """
        Process messages from the AppRunner and pass them to the app instance.

        Parameters
        ----------
        message : str
            The message to be processed.
        """
        self._app.received_signal_message(message)

    def _finish_processing(self):
        """
        Perform finishing touches after the processing has terminated.
        """
        self.__set_proc_widget_visibility_for_running(False)
        self.sig_processing_running.emit(False)
        QtWidgets.QApplication.instance().processEvents()
        logger.debug("WorkflowRunFrame: Finished processing")

    def __set_proc_widget_visibility_for_running(self, running: bool):
        """
        Set the visibility of all widgets which need to be updated for/after
        procesing

        Parameters
        ----------
        running : bool
            Flag whether the AppRunner is running and widgets shall be shown
            accordingly or not.
        """
        self._widgets["but_exec"].setEnabled(not running)
        self._widgets["but_abort"].setVisible(running)
        self._widgets["but_abort"].setEnabled(running)
        self._widgets["progress"].setVisible(running)
        self._widgets["but_export_all"].setEnabled(not running)
        self._widgets["but_export_current"].setEnabled(not running)

    def __update_autosave_widget_visibility(self):
        """
        Update the visibility of the autosave widgets based on the selection
        of the autosae_results Parameter.
        """
        _vis = self.get_param_value("autosave_results")
        for _key in ["autosave_directory", "autosave_format"]:
            self.toggle_param_widget_visibility(_key, _vis)
