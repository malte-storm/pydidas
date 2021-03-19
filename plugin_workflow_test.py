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
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

p = 'h:/myPython'
if not p in sys.path:
    sys.path.insert(0, p)

import plugin_workflow_gui as pwg


PLUGIN_COLLECTION = pwg.PluginCollection()
WorkflowTree = pwg.WorkflowTree()
PALETTES = pwg.PALETTES
STYLES = pwg.STYLES

class _GuiWorkflowTreeNode(pwg.generic_tree.GenericNode):
    width = 300
    height = 60
    child_spacing = 20
    border_spacing = 10

    def __init__(self, parent=None, node_id=None):
        self.parent = parent
        self.node_id = node_id
        self._children = []

    def get_width(self):
        if len(self._children) == 0:
            return self.width
        w = (len(self._children) - 1) * self.child_spacing
        for child in self._children:
            w += child.get_width()
        return w

    def get_height(self):
        if len(self._children) == 0:
            return self.height
        h = []
        for child in self._children:
            h.append(child.get_height())
        return max(h) + self.child_spacing + self.height

    def get_relative_positions(self):
        pos = {self.node_id: [0, 0]}

        if not self.is_leaf():
            child_w = {}

            for child in self._children:
                child_w[child.node_id] = child.get_width()

            w = (np.sum([_w[1] for _w in child_w.items()])
                 + (len(self._children) - 1) * self.child_spacing)
            dx = w // (len(self._children) - 1)
            x0 = - w // 2

            for i, child in enumerate(self._children):
                _p = child.get_relative_positions()
                for key in _p:
                    pos.update([_p[key][0] - x0 + i * dx,
                                _p[key][1] + self.height + self.child_spacing])
            return pos


class _GuiWorkflowTreeManager:
    def __init__(self, qt_parent=None):
        self.root = None
        self.qt_parent = qt_parent

        self.node_pos = {}
        self.widgets = {}
        self.nodes = {}
        self.node_ids = []
        self.active_node = None


    def add_plugin_node(self, name, title=None):
        if not self.root:
            _newid = 0
        else:
            _newid = self.node_ids[-1] + 1

        title = title if title else name
        widget = WorkflowPluginWidget(self.parent_widget, title, name, _newid)
        node = _GuiWorkflowTreeNode(self.active_node, _newid)
        if not self.root:
            self.root = node

        self.nodes[_newid] = node
        self.widgets[_newid] = widget

        self.node_ids.append(_newid)
        self.active_node = node

    def get_node_positions(self):
        if not self.root:
            raise KeyError('No root node specified')
        _pos = self.root.get_relative_positions()
        _n = len(_pos)

        pos_ids = []
        pos_vals = []
        for key, pos in _pos.items():
            pos_ids.append(key)
            pos_vals.append(pos)
        pos_ids = np.asarray(pos_ids)
        pos_vals = np.asaray(pos_vals)
        print(pos_ids, pos_vals)



class WorkflowPluginWidget(QtWidgets.QFrame):
    def __init__(self, qt_parent=None, title='No title',
                 name=None, widget_id=None, position=None):
        super().__init__(qt_parent)
        self.qt_parent = qt_parent
        # self.qt_main = qt_main
        self.position = position

        if not name:
            raise ValueError('No plugin name given.')
        if not widget_id:
            raise ValueError('No plugin node id given.')

        self.plugin = PLUGIN_COLLECTION.get_plugin_by_name(name)()

        self.setFixedSize(300, 60)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setLineWidth(2)
        self.setAutoFillBackground(True)
        self.setPalette(PALETTES['workflow_plugin_widget'])

        self.qtw_title = QtWidgets.QLabel(title, self)
        self.qtw_title.setStyleSheet(STYLES['plugin_title'])
        self.qtw_title.setGeometry(4, 2, 224, 22)

        self.qtw_del_button = QtWidgets.QPushButton('delete plugin', self)
        self.qtw_del_button.setStyleSheet(STYLES['plugin_del_button'])
        self.qtw_del_button.setGeometry(228, 2, 70, 22)

        self.qtw_cfg_button = QtWidgets.QPushButton('Configure plugin', self)
        self.qtw_cfg_button.setGeometry(2, 33, 296, 25)

        self.qtw_del_button.clicked.connect(partial(self.msg, 'Clicked del button'))
        self.qtw_cfg_button.clicked.connect(partial(self.msg, 'Clicked cfg button'))

    def mousePressEvent(self, event):
        print('Clicked widget')

    def msg(self, msg):
        print(msg)

    def widget_select(self):
        self.setLineWidth(4)

    def widget_deselect(self):
        self.setLineWidth(2)


class WorkflowTreeCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        #self.setFixedSize(800, 600)


        self.setAutoFillBackground(True)
        self.setPalette(PALETTES['workflow_widget'])

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        # self._layout.addWidget(WorkflowPluginWidget(self, self.parent, 'Test', 'HDF loader', 1))
        # self._layout.addWidget(WorkflowPluginWidget(self, self.parent, 'Test', 'HDF loader', 1))
        # self._layout.addWidget(WorkflowPluginWidget(self, self.parent, 'Test', 'HDF loader', 1))
        # self._layout.addWidget(WorkflowPluginWidget(self, self.parent, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))
        # self._layout.addWidget(WorkflowPluginWidget(self, 'Test', 'HDF loader', 1))

        self.setLayout(self._layout)

        self.buttons = []
        #grid in 30 x 120 pixel steps from (15, 585) x (5, 795)
        self.grid = np.zeros((59, 79))

    def find_empty_spot(self, x, y):
        return

    def dragEnterEvent(self, e):
        e.accept()

    def DragMoveEvent (self, e):
        # if
        pos_x = e.pos().x()
        pos_y = e.pos().y()
        print(pos_x, pos_y)
        if not self.grid[pos_y, pos_x]:
            print(pos_x, pos_y)
            e.accept()
        else:
            print('no good')
        e.ignore()

    def dropEvent(self, e):
        index = self.parent.treeView.selectedIndexes()[0]
        model = index.model()
        #filter headings:
        if model.itemFromIndex(index).parent() is None:
            e.ignore()
            return

        self.buttons.append(QtWidgets.QPushButton('test button'))
        i_button = len(self.buttons)
        #self.buttons[i_button].clicked.connect(partial(self.parent.button_clicked, i_button))
        # self.

        index = self.parent.treeView.selectedIndexes()[0]
        name = index.model().itemFromIndex(index).text()
        if self.parent.process == None:
            pass
        pos_x = (e.pos().x() - 5) // 10
        pos_y = (e.pos().y() - 5) // 10
        if self.grid[pos_y, pos_x]:
            pos_x, pos_y = self.find_empty_spot(pos_x, pos_y)

        index = self.parent.treeView.selectedIndexes()[0]
        name = index.model().itemFromIndex(index).text()
        print(name, pos_x, pos_y)
        if not self.grid[pos_y, pos_x]:
            pass
        # print(e.mimeData().parent(), e.mimeData().__str__())
        # for item in inspect.getmembers(e.mimeData()):
        #     print(item)

class _WorkflowScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None, widget=None):
        super().__init__(parent)
        self.parent = parent
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setFixedHeight(600)
        self.setFixedWidth(800)


class LayoutTest(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.status = self.statusBar()

        self.main_frame = QtWidgets.QWidget()
        self.setCentralWidget(self.main_frame)
        self.status.showMessage('Test status')
        _layout = QtWidgets.QVBoxLayout()
        _layout.setContentsMargins(5, 10, 10, 10)

        self.workflow_edit_manager = _GuiWorkflowTreeManager(self)
        self.workflow_canvas = WorkflowTreeCanvas()
        self.treeView = pwg.widgets.PluginTreeView(self)

        self.workflow_area = _WorkflowScrollArea(self, self.workflow_canvas)

        self.button1 = QtWidgets.QPushButton('Test button')
        self.label1 = QtWidgets.QLabel('test label 1')
        _layout.addWidget(self.label1)
        _layout.addWidget(self.button1)
        _layout.addWidget(self.workflow_area)
        _layout.addWidget(QtWidgets.QLabel('Available'))
        _layout.addWidget(self.treeView)

        self.setWindowTitle('Layout test')
        self.main_frame.setLayout(_layout)



    def button_clicked(self, i_button):
        print(f'clicked button {i_button}')



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = LayoutTest()
    gui.show()
    sys.exit(app.exec_())