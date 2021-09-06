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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettingsFrame']

import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore


from pydidas.core import ScanSettings
from pydidas.widgets import CreateWidgetsMixIn, excepthook, BaseFrame
from pydidas.widgets.parameter_config import ParameterConfigWidgetsMixIn
from pydidas.gui.builders.scan_settings_frame_builder import (
    create_scan_settings_frame_widgets_and_layout)

SCAN_SETTINGS = ScanSettings()


class ScanSettingsFrame(BaseFrame, ParameterConfigWidgetsMixIn,
                        CreateWidgetsMixIn):
    """
    Frame for managing the global scan settings.
    """
    TEXT_WIDTH = 180
    PARAM_INPUT_WIDTH = 120

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent,name=name)
        ParameterConfigWidgetsMixIn.__init__(self)

        create_scan_settings_frame_widgets_and_layout(self)
        self.toggle_dims()

    def toggle_dims(self):
        _prefixes = ['scan_dir_{n}', 'n_points_{n}', 'delta_{n}',
                     'unit_{n}', 'offset_{n}']
        _dim = int(self.param_widgets['scan_dim'].currentText())
        for i in range(1, 5):
            _toggle = True if i <= _dim else False
            self._widgets[f'title_{i}'].setVisible(_toggle)
            for _pre in _prefixes:
                self.param_widgets[_pre.format(n=i)].setVisible(_toggle)
                self.param_textwidgets[_pre.format(n=i)].setVisible(_toggle)

    def update_param(self, param_ref, widget):
        """
        Overload the update of a parameter method to handle the linked
        X-ray energy / X-ray wavelength variables.

        Parameters
        ----------
        param_ref : str
            The Parameter reference key
        widget : pydidas.widgets.parameter_config.InputWidget
            The widget used for the I/O of the Parameter value.
        """
        try:
            SCAN_SETTINGS.set(param_ref, widget.get_value())
        except Exception:
            widget.set_value(SCAN_SETTINGS.get(param_ref))
            excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if param_ref == 'xray_wavelength':
            _w = self.param_widgets['xray_energy']
            _w.set_value(SCAN_SETTINGS.get('xray_energy'))
        elif param_ref == 'xray_energy':
            _w = self.param_widgets['xray_wavelength']
            _w.set_value(SCAN_SETTINGS.get('xray_wavelength') * 1e10)

if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       ScanSettingsFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
