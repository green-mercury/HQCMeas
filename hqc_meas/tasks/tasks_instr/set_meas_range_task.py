# -*- coding: utf-8 -*-
# =============================================================================
# module : set_meas_range_task.py
# author : Holger Graef
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Float, set_default, Str, Value
from time import sleep

from hqc_meas.tasks.api import InstrumentTask, InstrTaskInterface, InterfaceableTaskMixin


class SetMeasRangeTask(InstrumentTask):
    """Set measurement range on Bilt Voltmeter

    """
    #: Id of the channel to use.
    channel = Str("1").tag(pref=True)
    
    selected_range = Str().tag(pref=True)
    
    #: Reference to the driver for the channel.
    channel_driver = Value()

    driver_list = ['TinyBilt']
    range_list = ['0.05', '0.5', '5', '50']

    def perform(self):
        """
        """
        if not self.driver:
            self.start_driver()

        if not self.channel_driver:
            self.channel_driver = self.driver.get_channel(self.channel)
            
            self.channel_driver.vrange = self.selected_range

KNOWN_PY_TASKS = [SetMeasRangeTask]