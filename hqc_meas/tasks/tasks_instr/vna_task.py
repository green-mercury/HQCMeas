# -*- coding: utf-8 -*-
# =============================================================================
# module : vna_task.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Str, set_default

from hqc_meas.tasks.api import InstrumentTask
import numpy as np

class VNATask(InstrumentTask):
    """Get traces from Anritsu VNA
    """
    traces = Str('1,2,3,4').tag(pref=True)
    avgcount = Str('1').tag(pref=True)
    selected_avgtype = Str('Point').tag(pref=True)

    driver_list = ['AnritsuVNA']
    
    task_database_entries = set_default({'sweep_data': np.array([0])})

    def perform(self):
        """
        """
        if not self.driver:
            self.start_driver()
        
        vna = self.driver

        freqs = vna.get_freq_list()         # get frequency list
        vna.set_average(int(self.avgcount), vna.AVG_POINT_BY_POINT if self.selected_avgtype == 'Point' else vna.AVG_SWEEP_BY_SWEEP)
        vna.single_sweep()          # execute a single sweep (and wait until it's done)
        table = []
        table.append(freqs)
        for i in self.traces.split(','):
            sreal, simag = vna.get_trace(i)     # get real and imag part of i-th trace
            table.append(sreal)
            table.append(simag)
            
        self.write_in_database('sweep_data', np.transpose(np.asarray(table)))

KNOWN_PY_TASKS = [VNATask]