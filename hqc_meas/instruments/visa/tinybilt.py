# -*- coding: utf-8 -*-
#==============================================================================
# module : tinybilt.py
# author : Holger Graef and others
# license : MIT license
#==============================================================================
"""

This module defines drivers for TinyBilt using VISA library.

:Contains:
    TinyBiltChannel
    TinyBilt


"""
from threading import Lock
from contextlib import contextmanager
from ..driver_tools import (BaseInstrument, InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument
from visa import VisaTypeError
from textwrap import fill
from inspect import cleandoc
import re
import time
import numpy as np


class TinyBiltChannel(BaseInstrument):
    def __init__(self, TB, channelid, caching_allowed=True,
                 caching_permissions={}):
        super(TinyBiltChannel, self).__init__(None, caching_allowed,
                                              caching_permissions)
        self._TB = TB
        self._channel = channelid

    def reopen_connection(self):
        self._TB.reopen_connection()

    @contextmanager
    def secure(self):
        """ Lock acquire and release method

        """
        i = 0
        while not self._TB.lock.acquire():
            time.sleep(0.1)
            i += 1
            if i > 50:
                raise InstrIOError
        try:
            yield
        finally:
            self._TB.lock.release()



class BiltVSource(TinyBiltChannel):     # Bilt voltage source
#    def __init__(self, TB, channelid, caching_allowed=True,
#                 caching_permissions={}):
#        super(TinyBiltChannel, self).__init__(TB, channelid, caching_allowed,
#                                              caching_permissions)

    @instrument_property
    @secure_communication()
    def output(self):
        """ Output getter method

        """
        with self.secure():
            output = self._TB.ask_for_values('i{};OUTP?'
                                             .format(self._channel))[0]
            if output == 1:
                return 'ON'
            elif output == 0:
                return 'OFF'
            else:
                mes = 'TinyBilt did not return its output'
                raise InstrIOError(mes)

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method. 'ON', 'OFF'
        """
        with self.secure():
            on = re.compile('on', re.IGNORECASE)
            off = re.compile('off', re.IGNORECASE)
            if value == 1 or on.match(str(value)):

                self._TB.write('i{};OUTP1'.format(self._channel))
                if self._TB.ask_for_values('i{};OUTP?'
                                           .format(self._channel))[0] != 1:
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            elif value == 0 or off.match(str(value)):
                self._TB.write('i{};OUTP0'.format(self._channel))
                if self._TB.ask_for_values('i{};OUTP?'
                                           .format(self._channel))[0] != 0:
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            else:
                mess = fill(cleandoc('''The invalid value {} was sent to
                            switch_on_off method''').format(value), 80)
                raise VisaTypeError(mess)

    @instrument_property
    @secure_communication()
    def big_volt_range(self):
        """Voltage range getter method. Two values possible :
        big range = 12V and small range = 1.2V
        """
        with self.secure():
            voltage = self._TB.ask_for_values('i{};volt:rang?'
                                              .format(self._channel))[0]
            if voltage is not None:
                return voltage
            else:
                raise InstrIOError

    @big_volt_range.setter
    @secure_communication()
    def big_volt_range(self, value):
        """Voltage range method. Two values possible :
        big range = 12V = 'True' or 1 and small range = 1.2V = 'False' or 0
        TinyBilt need to be turned off to change the voltage range
        """
        with self.secure():
            outp = self._TB.ask_for_values('OUTP?')[0]
            if outp == 1:
                raise InstrIOError(cleandoc('''TinyBilt need to be turned
                                                 off to change the voltage
                                                range'''))
            if value in ('True', 1):
                self._TB.write('i{};volt:rang 12'.format(self._channel))
                result = self._TB.ask_for_values('i{};volt:rang?'
                                                 .format(self._channel))[0]
                if abs(result - 12) > 10**-12:
                    mess = 'Instrument did not set correctly the range voltage'
                    raise InstrIOError(mess)
            elif value in ('False', 0):
                self._TB.write('i{};volt:rang 1.2'.format(self._channel))
                result = self._TB.ask_for_values('i{};volt:rang?'
                                                 .format(self._channel))[0]
                if abs(result - 1.2) > 10**-12:
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the range
                                                voltage'''))
            else:
                raise ValueError(cleandoc('''Big range 12V = "True"
                                          or 1, small range 1.2V
                                          = "False" or 0'''))

    @instrument_property
    @secure_communication()
    def max_voltage(self):
        """max voltage getter method
        """
        with self.secure():
            maxV = self._TB.ask_for_values('i{};volt:sat:pos?'
                                           .format(self._channel))[0]
            if maxV is not None:
                return maxV
            else:
                raise InstrIOError

    @max_voltage.setter
    @secure_communication()
    def max_voltage(self, value):
        """max voltage setter method
        """
        with self.secure():
            self._TB.write('i{};volt:sat:pos {}'.format(self._channel, value))
            maxiV = self._TB.ask_for_values('i{};volt:sat:pos?'
                                            .format(self._channel))[0]
            if abs(maxiV - value) > 10**-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the maximum
                                            voltage'''))

    @instrument_property
    @secure_communication()
    def min_voltage(self):
        """min voltage getter method
        """
        with self.secure():
            minV = self._TB.ask_for_values('i{};volt:sat:neg?'
                                           .format(self._channel))[0]
            if minV is not None:
                return minV
            else:
                raise InstrIOError

    @min_voltage.setter
    @secure_communication()
    def min_voltage(self, value):
        """min voltage setter method
        """
        with self.secure():
            self._TB.write('i{};volt:sat:neg {}'.format(self._channel, value))
            miniV = self._TB.ask_for_values('i{};volt:sat:neg?'
                                            .format(self._channel))[0]
            if abs(miniV - value) > 10**-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the minimum
                                            voltage'''))

    @instrument_property
    @secure_communication()
    def voltage(self):
        """output value getter method
        """
        with self.secure():
            outp_val = self._TB.ask_for_values('i{};Volt?'
                                               .format(self._channel))[0]
            if outp_val is not None:
                return outp_val
            else:
                raise InstrIOError

    @voltage.setter
    @secure_communication()
    def voltage(self, value):
        """Output value setter method

        """
        with self.secure():
            # check if correct voltage is already set
            value = round(value,5)          # in order to avoid bad things happening when we define linspaces like (0,1,4): basically instrument does not seem to like too many figures
            result = round(self._TB.ask_for_values('i{};Volt?'.format(self._channel))[0], 5)
            if abs(result-value) < 1e-12:
                return
                
            # set new voltage otherwise
            self._TB.write('i{};Volt {}'.format(self._channel, value))
            
            time.sleep(0.05) # wait 50 ms for next check
            # wait for instrument to arrive at destination voltage
            status = self._TB.ask_for_values('i{};volt:status?'.format(self._channel))[0]
            while status != 1.0:        # TODO: timeout check here
                time.sleep(0.05) # wait 50 ms for next check
                status = self._TB.ask_for_values('i{};volt:status?'.format(self._channel))[0]
            
            # check if correct voltage is set
            result = round(self._TB.ask_for_values('i{};Volt?'.format(self._channel))[0], 5)
            if abs(result-value) > 1e-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the output
                                            value {}'''.format(value)))

    @secure_communication()
    def smooth_change(self, volt_destination, volt_step, time_step):
        """ Set a ramp from the present voltage
            to the volt_destination by step of volt_step
            with time of time_step between each step
        """
        with self.secure():
            present_voltage = round(self.voltage, 5)
            while abs(round(present_voltage - volt_destination,
                            5)) >= volt_step:
                time.sleep(time_step)
                self.voltage = present_voltage+volt_step*np.sign(volt_destination-present_voltage)

            self.voltage = volt_destination

class BiltMCVMeter(TinyBiltChannel):    # Bilt multichannel voltmeter
    @secure_communication()
    def read_voltage_dc(self):
        instrNum, chanNum = str.split(self._channel, ':')
        voltage = self._TB.ask_for_values("I{};C{};MEAS?".format(instrNum, chanNum))[0]
        if not voltage:
            raise InstrIOError(cleandoc('''Could not get voltage measurement from
            TinyBilt'''))
        else:
            return voltage
    
    @instrument_property
    @secure_communication()
    def vrange(self):
        """getter method for voltage range
        """
        with self.secure():
            instrNum, chanNum = str.split(self._channel, ':')
            result = self._TB.ask_for_values("I{};C{};MEAS:RANG?".format(instrNum, chanNum))
            if result is not None:
                return result
            else:
                raise InstrIOError

    @vrange.setter
    @secure_communication()
    def vrange(self, value):
        """setter method for voltage raneg
        """
        with self.secure():
            instrNum, chanNum = str.split(self._channel, ':')
            self._TB.write('I{};C{};MEAS:RANG {}'.format(instrNum, chanNum, value))
            

class TinyBilt(VisaInstrument):
    """
    """
    caching_permissions = {'defined_channels': True}

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super(TinyBilt, self).__init__(connection_info, caching_allowed,
                                       caching_permissions, auto_open)
        self.channels = {}
        self.lock = Lock()

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`
        """
        para['term_chars'] = '\n'
        super(TinyBilt, self).open_connection(**para)

    @secure_communication()
    def get_channel(self, channelid):
        """
        """
        if channelid not in self.defined_channels:
            return None

        if channelid in self.channels:
            return self.channels[channelid]
        else:
            instrType = self.get_instrument_type(channelid)
            if instrType == 2101:      # single channel voltage source
                channel = BiltVSource(self, channelid)
            elif instrType == 4082:      # multichannel voltmeter 
                channel = BiltMCVMeter(self, channelid)
            else:
                raise InstrIOError(cleandoc('''Unsupported instrument type: {}'''.format(instrType)))
            self.channels[channelid] = channel
            return channel

    @instrument_property
    @secure_communication()
    def defined_channels(self):
        """
        """
        channels = self.ask_for_values('I:L?') # return channel, id, channel, id, ...
        if channels:
            defined_channels = []
            for c in range(len(channels)/2):
                if channels[c*2+1] == 4082:          # identifies four-channel voltmeter
                    for i in range(4):
                        defined_channels.append('{}:{}'.format(int(channels[c*2]), i+1))
                else:
                    defined_channels.append('{}'.format(int(channels[c*2])))
            
            return defined_channels
        else:
            raise InstrIOError(cleandoc('''Instrument did not return
                                            the defined channels'''))
    
    @secure_communication()
    def get_instrument_type(self, channelid):
        instrnum = int(str.split(channelid, ':')[0])
        if channelid not in self.defined_channels:
            return None
        instrID = int(self.ask_for_values('I{};*idn?'.format(instrnum))[0])
        if not instrID:
            raise InstrIOError(cleandoc('''Instrument did not return channel ID'''))
        else:
            return instrID


DRIVERS = {'TinyBilt': TinyBilt}
