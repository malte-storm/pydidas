from base_plugins import ProcPlugin, PROC_PLUGIN

class AzimuthalIntegration(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'Azimuthal integration'
    params = {'beam_cente_x': None,
              'beam_cente_y': None,
              'bins': None,
              'theta_min': None,
              'theta_max': None,
              }

    def __init__(self):
        pass


    def execute(self, *data, **kwargs):
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        return np.array(np.sum(data)), kwargs