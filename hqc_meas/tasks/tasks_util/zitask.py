# -*- coding: utf-8 -*-
# =============================================================================
# module : meas_dc_tasks.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import set_default

from ..base_tasks import SimpleTask

import zhinst.ziPython, zhinst.utils
import numpy as np


class ZITask(SimpleTask):
    """Get current Vrms value from ZI Lockin
    """
    
    task_database_entries = set_default({'Vrms': 0.0})
        
    def perform(self):
        """
        """
        daq = zhinst.ziPython.ziDAQServer('localhost', 8005)
        device = zhinst.utils.autoDetect(daq)
        sample = daq.getSample('/'+device+'/demods/0/sample')
        r = np.sqrt(sample['x']**2+sample['y']**2)
        self.write_in_database('Vrms', r)

KNOWN_PY_TASKS = [ZITask]