# -*- coding: utf-8 -*-
# =============================================================================
# module : meas_dc_tasks.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import set_default
from time import time

from ..base_tasks import SimpleTask


class TimeTask(SimpleTask):
    """Get current time stamp

    """
    
    task_database_entries = set_default({'time': 0.0})

    def perform(self):
        """
        """
        self.write_in_database('time', time())

KNOWN_PY_TASKS = [TimeTask]