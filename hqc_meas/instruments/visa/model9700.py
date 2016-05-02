# -*- coding: utf-8 -*-
#==============================================================================
# module : anritsu_vna.py
# author : Holger Graef and Andreas Inhofer
# license : MIT license
#==============================================================================
"""

This module defines drivers for Anritsu Vector Star MS4644B using VISA library.

:Contains:
    Model9700


"""
from ..driver_tools import secure_communication, instrument_property
from ..visa_tools import VisaInstrument
#import visa
#import struct

class Model9700(VisaInstrument):
    """
    """
    _channel = 1   

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`
        """
        super(Model9700, self).open_connection(**para)

    @instrument_property
    @secure_communication()
    def ask_temperatures(self):
        '''
        This function gets the two temperatures of the temperature controller.
        '''
        TA = self.ask_for_values('TA?')[0]
        TB = self.ask_for_values('TB?')[0]
        return TA, TB
        
    
    @instrument_property
    @secure_communication()
    def ask_TA(self):
        '''
        This function gets the two temperatures of the temperature controller.
        '''
        return self.ask_for_values('TA?')[0]
    
    
    @instrument_property
    @secure_communication()
    def ask_TB(self):
        '''
        This function gets the two temperatures of the temperature controller.
        '''
        return self.ask_for_values('TB?')[0]

DRIVERS = {'Model9700': Model9700}
