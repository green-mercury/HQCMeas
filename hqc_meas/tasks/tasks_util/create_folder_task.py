# -*- coding: utf-8 -*-
# =============================================================================
# module : sleep_task.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import (Unicode)

import os

from ..base_tasks import SimpleTask


class CreateFolderTask(SimpleTask):
    """
    Creates folders.
    """

    folder_name = Unicode().tag(pref=True)

    def check(self, *args, **kwargs):
        """ Create Folder.

        """
        folder = self.format_string(self.folder_name)
        if not os.path.exists(folder):
            os.makedirs(folder)

        return True, {}
    
    def perform(self):
        pass


KNOWN_PY_TASKS = [CreateFolderTask]
