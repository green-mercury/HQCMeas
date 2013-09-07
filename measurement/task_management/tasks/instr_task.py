# -*- coding: utf-8 -*-
"""
"""
from traits.api import (Str, List, Instance, Dict)
from visa import Instrument, VisaIOError
from configobj import ConfigObj
import os

from .base_tasks import SimpleTask
from ...instruments.drivers import drivers
from ...instruments.profiles import profiles_folder_path
from ...instruments.instrument_manager import InstrumentManager

class InstrumentTask(SimpleTask):
    """
    """
    profile_dict = Dict(Str, Str, preference = True)
    profile_list = List(Str)
    selected_profile = Str(preference = True)
    driver_list = []
    selected_driver = Str(preference = True)
    driver = Instance(Instrument)

    def check(self, *args, **kwargs):
        """
        """
        profile = self.profile_dict[self.selected_profile]
        full_path = os.path.join(profiles_folder_path,
                                    profile)
        if not os.path.isfile(full_path):
            print 'Failed to get the specified instr profile in {}'.format(
                                                                self.task_name)
            return False

        if drivers.has_key(self.selected_driver):
            driver_class = drivers[self.selected_driver]
        else:
            print 'Failed to get the specified instr driver in {}'.format(
                                                                self.task_name)
            return False

        if kwargs['test_instr']:
            config = ConfigObj(full_path)
            if config['additionnal_mode'] != '':
                connection_str = config['connection_type']\
                                 + '::' + config['address']\
                                 + '::' + config['additionnal_mode']
            else:
                connection_str = config['connection_type']\
                                 + '::' + config['address']
            try:
                instr = driver_class(connection_str)
                instr.close()
            except VisaIOError:
                print 'Failed to establish the connection\
                    with the selected instrument in {}'.format(self.task_name)
                return False
        return True

    def start_driver(self):
        """
        """
        profile = self.profile_dict[self.selected_profile]
        full_path = os.path.join(profiles_folder_path, profile)
        driver_class = drivers[self.selected_driver]
        config = ConfigObj(full_path)

        if config['additionnal_mode'] != '':
            connection_str = config['connection_type']\
                                 + '::' + config['address']\
                                 + '::' + config['additionnal_mode']
        else:
            connection_str = config['connection_type']\
                             + '::' + config['address']

        self.driver = driver_class(connection_str)
        instrs = self.task_database.get_value('root', 'instrs')
        instrs.append(self.driver)
        self.task_database.set_value('root', 'instrs', instrs)

    def stop_driver(self):
        """
        """
        self.driver.close()

    def _profile_dict_changed(self):
        """
        """
        self.profile_list = self.profile_dict.keys()

    def _selected_driver_changed(self, new):
        """
        """
        manager = InstrumentManager()
        self.profile_dict = manager.matching_instr_list(new)