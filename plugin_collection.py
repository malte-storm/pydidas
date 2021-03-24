# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:13:34 2021

@author: ogurreck
"""
import importlib
import os
import inspect
import sys

INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

class _PluginCollectionFactory:
    """
    Singleton factory to make sure that only one PluginCollection exists
    at runtime.
    """
    def __init__(self):
        self._instance = None

    def __call__(self, plugin_path=None):
        if not self._instance:
            self._instance = _PluginCollection(plugin_path)
        return self._instance

PluginCollection = _PluginCollectionFactory()


class _PluginCollection:
    """
    Class to hold references of all plugins
    """

    def __init__(self, plugin_path=None):
        """
        Setup method.

        Parameters
        ----------
        directory : str, optional
            The search directory for plugins. The default is None.

        Returns
        -------
        None.

        """
        if not plugin_path:
            plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
        self.plugins = dict(base={}, proc={}, input={}, output={})
        # self.plugins['base'] = {}
        # self.plugins['proc'] = {}
        # self.plugins['input'] = {}
        # self.plugins['output'] = {}
        self.plugin_names = []
        self.plugin_classnames = []
        self.find_plugins(plugin_path)

    def find_files(self, path):
        """
        Search for all python files in path.

        This method will search the specified path recursicely for all
        python files.

        Parameters
        ----------
        path : str
            The file system path to search.
        rel_path : str
            The relative path (if recursing). Default is None.

        Returns
        -------
        None.

        """
        path = path if not os.path.isfile(path) else os.path.dirname(path)
        _results = []
        _entries = [os.path.join(path, item) for item in os.listdir(path)
                   if (item[:2] != '__' and item[0] != '.')]
        _dirs = [item for item in _entries if os.path.isdir(item)]
        _files = [item for item in _entries if os.path.isfile(item)]
        for entry in _dirs:
            _results += self.find_files(os.path.join(path, entry))
        _results += [item for item in _files
                     if (item[:2] != '__' and item[0] != '.' and
                         item[-3:] == '.py')]
        return _results

    def find_plugins(self, path, reload=True):
        """
        TO DO
        """

        path = path if not os.path.isfile(path) else os.path.dirname(path)
        _modules = [item[len(path)+len(os.sep):-3].replace(os.sep, '.')
                  for item in self.find_files(path)]
        if len(_modules) == 0:
            return
        for _mod in _modules:
            spec = importlib.util.find_spec(_mod)
            _m = spec.loader.load_module()
            clsmembers = inspect.getmembers(_m, inspect.isclass)
            for _name, _cls in clsmembers:
                if not self.plugin_consistency_check(_cls):
                    continue
                if (_name in self.plugin_names or
                    _cls.__name__ in self.plugin_classnames) and not reload:
                    raise NameError(f'Plugin with name "{_name}" and '
                                    f'class name {_cls.__name__} already'
                                    'exists in plugin catalogue.')
                ptype = self.plugin_type_check(_cls)
                if (_name not in self.plugins[ptype] or reload):
                    self.plugins[ptype][_name] = _cls
                    if _name not in self.plugin_names:
                        self.plugin_names.append(_name)
                    if _cls.__name__ not in self.plugin_classnames:
                        self.plugin_names.append(_cls.__name__)
            del _m

    @staticmethod
    def plugin_type_check(cls_item):
        """
        TO DO
        """
        if cls_item.basic_plugin:
            return 'base'
        if cls_item.plugin_type == INPUT_PLUGIN:
            return 'input'
        if cls_item.plugin_type == PROC_PLUGIN:
            return 'proc'
        if cls_item.plugin_type == OUTPUT_PLUGIN:
            return 'output'
        raise ValueError('Could not determine the plugin type for'
                         'class "{cls_item.__name__}"')

    @staticmethod
    def plugin_consistency_check(cls_item):
        """
        Verify that plugins pass a rudimentary sanity check.

        Parameters
        ----------
        cls_item : plugin object
            A plugin object.

        Returns
        -------
        bool.
            Returns True if consistency check succeeded and False otherwise.
        """
        if (hasattr(cls_item, 'basic_plugin') and
            hasattr(cls_item, 'plugin_type') and
            hasattr(cls_item, 'plugin_name') and
            hasattr(cls_item, 'execute')):
            return True
        return False

    def get_all_plugins(self):
        """
        TO DO
        """
        _d = {**self.plugins['input'], **self.plugins['proc'],
              **self.plugins['output']}
        _res = []
        for item in _d.values():
            _res.append(item)
        del _d
        return _res

    def get_all_plugin_names(self):
        """
        TO DO
        """
        _d = {**self.plugins['input'], **self.plugins['proc'],
              **self.plugins['output']}
        _res = []
        for item in _d.values():
            _res.append(item.plugin_name)
        del _d
        return _res


    def get_plugin_by_name(self, name):
        """
        TO DO
        """
        for _plugin in self.get_all_plugins():
            if name == _plugin.plugin_name:
                return _plugin
        raise KeyError(f'No plugin with name "{name}" has been registered!')

    def get_plugin_by_class_name(self, name):
        """
        TO DO
        """
        for _plugin in self.get_all_plugins():
            if name == _plugin.__name__:
                return _plugin
        raise KeyError(f'No plugin with claass name "{name}" has been '
                       'registered!')
