# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import inspect
import os
import numpy as np
from functools import partial
from copy import copy
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

p = 'h:/myPython'
if not p in sys.path:
    sys.path.insert(0, p)

import plugin_workflow_gui as pwg


PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
#WorkflowTree = pwg.WorkflowTree()

class WorkflowTreeCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.title = QtWidgets.QLabel(self)
        self.title.setStyleSheet(STYLES['title'])
        self.title.setText('Workflow tree')
        self.title.move(10, 10)
        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)

        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self.widget_connections = []


    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 2))
        self.draw_connections()
        self.painter.end()

    def draw_connections(self):
        for x0, y0, x1, y1 in self.widget_connections:
            self.painter.drawLine(x0, y0, x1, y1)


    def update_widget_connections(self, widget_conns):
        self.widget_connections = widget_conns
        self.update()

class PluginEditCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)

        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)

    # def paint_connections(self, *points):


class _ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None, widget=None, width=None, height=None):
        super().__init__(parent)
        self.parent = parent
        self.setWidget(widget)
        self.setWidgetResizable(True)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)


class WorkflowEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, qt_main=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self.workflow_canvas = WorkflowTreeCanvas(self)
        self.plugin_edit_canvas = PluginEditCanvas(self)
        self.treeView = pwg.widgets.WidgetTreeviewForPlugins(self.qt_main)
        self.workflow_area = _ScrollArea(
            self, self.workflow_canvas,
            self.qt_main.params['workflow_edit_canvas_x'],
            self.qt_main.params['workflow_edit_canvas_y']
        )
        self.plugin_edit_area = _ScrollArea(self, self.plugin_edit_canvas, 400, None)
        self.plugin_text_hint = PluginTextHint(self)

        self.treeView.doubleClicked.connect(self.treeview_add_plugin)
        self.treeView.selection_changed_signal.connect(self.treeview_clicked_plugin)

        _layout0 = QtWidgets.QHBoxLayout()
        _layout0.setContentsMargins(5, 5, 5, 5)

        _layout1 = QtWidgets.QVBoxLayout()
        _layout1.addWidget(self.workflow_area)

        _layout2 = QtWidgets.QHBoxLayout()
        _layout2.addWidget(self.treeView)
        _layout2.addWidget(self.plugin_text_hint)
        _layout1.addLayout(_layout2)

        _layout0.addLayout(_layout1)
        _layout0.addWidget(self.plugin_edit_area)
        self.setLayout(_layout0)


    def treeview_add_plugin(self, index):
        item = self.treeView.selectedIndexes()[0]
        name = item.model().itemFromIndex(index).text()
        self.qt_main.workflow_edit_manager.add_plugin_node(name)

    @QtCore.pyqtSlot(str)
    def treeview_clicked_plugin(self, name):
        if name in ['Input plugins', 'Processing plugins', 'Output plugins']:
            return
        p = PLUGIN_COLLECTION.get_plugin_by_name(name)()
        self.plugin_text_hint.setText(p.get_hint_text(), p.plugin_name)
        del p


class PluginTextHint(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptRichText(True)
        self.setReadOnly(True)

    def setText(self, text, title=None):
        super().setText('')
        if title:
            self.setFontPointSize(14)
            self.setFontWeight(75)
            self.append(f'Plugin description: {title}')
        self.setFontPointSize(10)
        self.append('')
        for key, item in text:
            self.setFontWeight(75)
            self.append(key + ':')
            self.setFontWeight(50)
            item = '    ' + item if key != 'Parameters' else  item
            self.append('    ' + item if key != 'Parameters' else  item)


class ExperimentEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, qt_main=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main


class MainTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)


class LayoutTest(QtWidgets.QMainWindow):
    name_selected_signal = QtCore.pyqtSlot(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.params = {'workflow_edit_canvas_x': 1000,
                       'workflow_edit_canvas_y': 600}
        self.status = self.statusBar()

        self.workflow_edit_manager = pwg.gui.GuiWorkflowEditTreeManager()


        self.main_frame = QtWidgets.QTabWidget()
        self.setCentralWidget(self.main_frame)
        self.status.showMessage('Test status')


        self.experiment_edit_tab = ExperimentEditTab(self.main_frame, self)
        self.workflow_edit_tab = WorkflowEditTab(self.main_frame, self)
        self.main_frame.addTab(self.experiment_edit_tab, 'Experiment editor')
        self.main_frame.addTab(self.workflow_edit_tab, 'Workflow editor')
        self.workflow_edit_manager.update_qt_items(
            self.workflow_edit_tab.workflow_canvas, self
        )

        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 0')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 1')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 2')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 3')
        self.workflow_edit_manager.set_active_node(2)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 4')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 5')
        self.workflow_edit_manager.set_active_node(2)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 6')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 7')
        self.workflow_edit_manager.set_active_node(6)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 8')

        self.setWindowTitle('Plugin edit test')
        self._createMenu()

    def _createMenu(self):
        self._menu = self.menuBar()
        fileMenu = QtWidgets.QMenu('&File')
        self._menu.addMenu(fileMenu)
        self._menu.addMenu("&Edit")
        self._menu.addMenu("&Help")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = LayoutTest()
    gui.show()
    sys.exit(app.exec_())