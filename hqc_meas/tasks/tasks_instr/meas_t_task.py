# -*- coding: utf-8 -*-
# =============================================================================
# module : meas_dc_tasks.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Float, set_default, Str, Value
from time import sleep

from hqc_meas.tasks.api import InstrumentTask


class MeasTemperatureTask(InstrumentTask):
    """Measure a temperature

    """

    driver_list = ['Model9700']
    
    task_database_entries = set_default({'tempA': 0.0, 'tempB': 0.0})

    def perform(self):
        """
        """
        if not self.driver:
            self.start_driver()

        tempA, tempB = self.driver.ask_temperatures
        self.write_in_database('tempA', tempA)
        self.write_in_database('tempB', tempB)

KNOWN_PY_TASKS = [MeasTemperatureTask]