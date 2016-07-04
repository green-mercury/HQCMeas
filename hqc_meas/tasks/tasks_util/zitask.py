# -*- coding: utf-8 -*-
# =============================================================================
# module : meas_dc_tasks.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import set_default

from ..base_tasks import SimpleTask

import zhinst.ziPython, zhinst.utils
import numpy as np

from atom.api import Bool, Instance, Str

class ZITask(SimpleTask):
    """Get current Vrms value from ZI Lockin
    """
    
    task_database_entries = set_default({'Vrms': 0.0, 'sigmaVrms': 0.0})
  
    ZIinitialised = Bool(False)
    daq = Instance(zhinst.ziPython.ziDAQServer)
    device = Str()
    
    def perform(self):
        """
        """
#        daq = zhinst.ziPython.ziDAQServer('localhost', 8005)
#        device = zhinst.utils.autoDetect(daq)
#        sample = daq.getSample('/'+device+'/demods/0/sample')
#        r = np.sqrt(sample['x']**2+sample['y']**2)
#        self.write_in_database('Vrms', r)
        
            #clean queue
        c = str(0) # channel number minus one  
        polltime = 0.5
        
        if not self.ZIinitialised:      
            self.daq = zhinst.ziPython.ziDAQServer('localhost', 8005)
            self.device = zhinst.utils.autoDetect(self.daq)  
                        
            self.daq.flush()
            
            # Subscribe to scope
            path0 = '/' + self.device + '/demods/'+ c + '/sample'
            self.daq.subscribe(path0)
            self.ZIinitialised = True
    
        # Poll data 1s, second parameter is poll timeout in [ms] (recomended value is 500ms) 
        dataDict = self.daq.poll(polltime,500);
    
        # Unsubscribe to scope
        #daq.unsubscribe(path0)
    
        # Recreate data
        if self.device in dataDict:
            if dataDict[self.device]['demods'][c]['sample']['time']['dataloss']:
                print 'Sample loss detected.'
            else:
                data = dataDict[self.device]['demods'][c]['sample']
                rdata = np.sqrt(data['x']**2+data['y']**2)
                self.write_in_database('Vrms', np.mean(rdata))
                self.write_in_database('sigmaVrms', np.std(rdata))

KNOWN_PY_TASKS = [ZITask]