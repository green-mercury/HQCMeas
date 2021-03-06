# -*- coding: utf-8 -*-
#==============================================================================
# module : anritsu_vna.py
# author : Holger Graef and Andreas Inhofer
# license : MIT license
#==============================================================================
"""

This module defines drivers for Anritsu Vector Star MS4644B using VISA library.

:Contains:
    AnritsuVNA


"""
from ..driver_tools import secure_communication
from ..visa_tools import VisaInstrument
import visa
import struct
import warnings

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

    @secure_communication()
    def ask_values_anritsu(self, query_str):
        '''
        This function sends a query to the VNA and retrieves the returned values
        in the binary format that is specified in the Anritsu documentation.
        '''
        vi = self._driver.vi               # retrieve vi for vpp43 legacy stuff        
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=visa.VisaIOWarning)           # because we often leave data in buffer
            
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

    @secure_communication()
    def get_freq_list(self):
        return self.ask_values_anritsu(':SENS1:FREQ:DATA?;')
    
    @secure_communication()
    def get_trace(self, trace_num):
        '''
        Gets trace number trace_num from VNA.
        '''
        # select desired trace
        self.write(':CALC1:PAR{}:SEL;'.format(trace_num))
        assert int(self.ask(':CALC1:PAR:SEL?')) == int(trace_num)
        data = self.ask_values_anritsu(':CALC1:DATA:SDAT?')
        
        sreal = data[::2]
        simag = data[1::2]
        return sreal, simag
     
    @secure_communication()
    def single_sweep(self):
        '''
        This function starts a single sweep (VNA will hold at the end of the
        sweep) and waits for the sweep to be done.
        '''    
        self.write(':SENS1:HOLD:FUNC SING;')       # single sweep with hold
        self.write(':TRIG:SING;')                 # trigger single sweep

        timeout = self.timeout
        self.timeout = 120.
        
        self.ask('*STB?')           # ask for status byte (or whatever)        
        
        self.timeout = timeout
        
    @secure_communication()        
    def enable_averaging(self):
        self.write(':SENS1:AVER ON;')
    
    @secure_communication()
    def disable_averaging(self):
        self.write(':SENS1:AVER OFF;')
        
    @secure_communication()        
    def set_average_count(self, count):
        self.write(':SENS1:AVER:COUNT {}'.format(count))
        
    AVG_POINT_BY_POINT = 'POIN'
    AVG_SWEEP_BY_SWEEP = 'SWE'
    
    @secure_communication()
    def set_average_type(self, typ):
        self.write(':SENS1:AVER:TYP {}'.format(typ))
    
    @secure_communication()
    def set_average(self, count, typ):
        self.enable_averaging()
        self.set_average_count(count)
        self.set_average_type(typ)

DRIVERS = {'AnritsuVNA': AnritsuVNA}
