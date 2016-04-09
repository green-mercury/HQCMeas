# -*- coding: utf-8 -*-
#==============================================================================
# module : anritsu_vna.py
# author : Holger Graef and Andreas Inhofer
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
import visa
import struct

class AnritsuVNA(VisaInstrument):
    """
    """
    _channel = 1    
        
    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`
        """
        para['term_chars'] = '\n'
        
        super(AnritsuVNA, self).open_connection(**para)
        #Initialisation that apparently is needed. We should check the doc what the different commands do.
        self.write(r'*ESE 60;*SRE 48;*CLS;:FORM:BORD NORM;')
        # Make sure Data is communicated in the correct format.
        self.write(r':FORM:DATA ASC;') 
        # Check that everything works fine for the moment.
        #print self.ask('SYST:ERR?')

    def ask_values_anritsu(self, query_str):
        '''
        This function sends a query to the VNA and retrieves the returned values
        in the binary format that is specified in the Anritsu documentation.
        '''
        vi = self._driver.vi               # retrieve vi for vpp43 legacy stuff        
        
        self.clear()                        # empty buffer
        # make sure Data is communicated in the correct format.
        self.write(':FORM:DATA REAL;')      # switch data transmission to binary     
        # send query
        self.write(query_str)               # send query string
        # receive data
        self.term_chars = ''                # switch off termination char.
        header = visa.vpp43.read(vi, 2) # read header-header
        assert header[0] == '#'             # check if format is OK
        count = int(header[1])              # read length of header
        #print "Reading {} bytes header from Anritsu".format(count)
        header = visa.vpp43.read(vi, count) # read header
        count = int(header)                 # read length of binary data
        #print "Reading {} bytes data from Anritsu".format(count)
        self.term_chars = ''
        data = visa.vpp43.read(vi, count)     # this crashes Spyder if variable explorer is open !!
        visa.vpp43.read(vi, 1)    # read the termination character (do not do this when using GPIB)
        #print 'Successfully read {} bytes'.format(len(data))
        assert len(data) == count            # check all data was read
        self.term_chars = '\n'               # switch on term char
        self.write(':FORM:DATA ASC;')        # read data in ASCII format
        return struct.unpack('!'+'d'*(count/8), data) # convert data from big-endian binary doubles to array of python doubles

    def get_freq_list(self):
        return self.ask_values_anritsu(':SENS1:FREQ:DATA?;')
        
    def get_trace(self, trace_num):
        '''
        Gets trace number trace_num from VNA.
        '''
        # select desired trace
        self.write(':CALC1:PAR{}:SEL;'.format(trace_num)) 
        data = self.ask_values_anritsu(':CALC1:DATA:SDAT?')
        
        sreal = data[::2]
        simag = data[1::2]
        return sreal, simag
        
    def single_sweep(self):
        '''
        This function starts a single sweep (VNA will hold at the end of the
        sweep) and waits for the sweep to be done.
        '''
        self.write(':SENS:HOLD:FUNC SING;')       # single sweep with hold
        self.write(':TRIG:SING;')                 # trigger single sweep
        
        n = 0       # number of times we ask for status
        while True:
            try:
                n = n+1
                self.ask(':STAT:OPER:COND?')
            except visa.VisaIOError:
                print 'Still sweeping or connection lost'
                continue
            break
        
        for i in range(n-1): self.read()  # workaround that empties the read buffer
        
        print 'Sweep is done'
        
    def enable_averaging(self):
        self.write(':SENS1:AVER ON;')
    
    def disable_averaging(self):
        self.write(':SENS1:AVER OFF;')
        
    def set_average_count(self, count):
        self.write(':SENS1:AVER:COUNT {}'.format(count))
        
    AVG_POINT_BY_POINT = 'POIN'
    AVG_SWEEP_BY_SWEEP = 'SWE'
    def set_average_type(self, typ):
        self.write(':SENS1:AVER:TYP {}'.format(typ))
    
    def set_average(self, count, typ):
        self.enable_averaging()
        self.set_average_count(count)
        self.set_average_type(typ)

DRIVERS = {'AnritsuVNA': AnritsuVNA}
