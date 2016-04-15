# -*- coding: utf-8 -*-
# =============================================================================
# module : hqc_meas/tasks/task_instr/set_dc_voltage_task.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import (Float, Value, Str, set_default)

import time
import logging
from inspect import cleandoc

from hqc_meas.tasks.api import InstrumentTask


class SetDCOutputTask(InstrumentTask):
    """Switch on or off DC output on Bilt source.

    """
    selected_value = Str('ON').tag(pref=True)
    
    channel = Str("1").tag(pref=True)
    
    #: Reference to the driver for the channel.
    channel_driver = Value()

    driver_list = ['TinyBilt']

    def perform(self, value=None):
        """
        """
        if not self.driver:
            self.start_driver()

        if not self.channel_driver:
            self.channel_driver = self.driver.get_channel(self.channel)

        if self.channel_driver.owner != self.task_name:
            self.channel_driver.owner = self.task_name
            if hasattr(self.channel_driver, 'function') and\
                    self.channel_driver.function != 'VOLT':
                log = logging.getLogger()
                mes = cleandoc('''Instrument assigned to task {} is not
                    configured to output a voltage'''.format(self.task_name))
                log.fatal(mes)
                self.root_task.should_stop.set()

        self.channel_driver.output = self.selected_value

KNOWN_PY_TASKS = [SetDCOutputTask]

