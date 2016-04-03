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

from hqc_meas.tasks.api import InstrumentTask, InstrTaskInterface, InterfaceableTaskMixin


class MeasDCVoltageTask(InterfaceableTaskMixin, InstrumentTask):
    """Measure a dc voltage.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    driver_list = ['Agilent34410A', 'Keithley2000']
    task_database_entries = set_default({'voltage': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def i_perform(self):
        """
        """
        if not self.driver:
            self.start_driver()

        sleep(self.wait_time)

        value = self.driver.read_voltage_dc()
        self.write_in_database('voltage', value)

KNOWN_PY_TASKS = [MeasDCVoltageTask]

class MultiChannelVoltMeterInterface(InstrTaskInterface):
    """
    """
    has_view = True

    driver_list = ['TinyBilt']

    #: Id of the channel to use.
    channel = Str("1").tag(pref=True)

    #: Reference to the driver for the channel.
    channel_driver = Value()

    def perform(self, value=None):
        """
        """
        task = self.task
        if not task.driver:
            task.start_driver()

        if not self.channel_driver:
            self.channel_driver = task.driver.get_channel(self.channel)

        sleep(task.wait_time)
        
        value = self.channel_driver.read_voltage_dc()
        task.write_in_database('voltage', value)

INTERFACES = {'MeasDCVoltageTask': [MultiChannelVoltMeterInterface]}