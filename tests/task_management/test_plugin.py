# -*- coding: utf-8 -*-
from enaml.workbench.api import Workbench
import enaml
import os
import shutil
from configobj import ConfigObj

with enaml.imports():
    from hqc_meas.utils.core_manifest import HqcCoreManifest
    from hqc_meas.utils.state_manifest import StateManifest
    from hqc_meas.utils.pref_manifest import PreferencesManifest

# TODO This stuff cannot be completed before some tasks are refactored, as they
# are currently broken (InstrTask)

def setup_module():
    print __name__, ': setup_module() ~~~~~~~~~~~~~~~~~~~~~~'


def teardown_module():
    print __name__, ': teardown_module() ~~~~~~~~~~~~~~~~~~~'


class Test_TaskManagement(object):

    test_dir = ''

    @classmethod
    def setup_class(cls):
        print __name__, ': TestClass.setup_class() ----------'
        # Creating dummy directory for prefs (avoid prefs interferences).
        directory = os.path.dirname(__file__)
        cls.test_dir = os.path.join(directory, '_tests')
        os.mkdir(cls.test_dir)

        # Creating dummy default.ini file in utils.
        util_path = os.path.join(directory, '..', '..', 'hqc_meas', 'utils')
        def_path = os.path.join(util_path, 'default.ini')
        if os.path.isfile(def_path):
            os.rename(def_path, os.path.join(util_path, '__default.ini'))

        # Making the preference manager look for info in test dir.
        default = ConfigObj(def_path)
        default['folder'] = cls.test_dir
        default['file'] = 'default_test.ini'
        default.write()

        conf = ConfigObj(os.path.join(cls.test_dir, 'default_test.ini')
        conf['hqc_meas.task_manager'] = {}
        task_path = os.path.join(directory, '..', '..', 'hqc_meas', 'tasks')
        task_api = set(('base_tasks.py', 'instr_task.py', '))
        task_loading = [unicode('tasks.' + mod[:-3])
                        for mod in os.listdir(task_path)
                        if mod.endswith('.py') and mod not in ]
        # TODO create false preferences for the task manager to avoid loading
        # all tasks and users templates. (create False template and add a non
        # working task to check everything is well behaved)

    @classmethod
    def teardown_class(cls):
        print __name__, ': TestClass.teardown_class() -------'
         # Removing pref files creating during tests.
        shutil.rmtree(cls.test_dir)

        # Restoring default.ini file in utils
        directory = os.path.dirname(__file__)
        util_path = os.path.join(directory, '..', '..', 'hqc_meas', 'utils')
        def_path = os.path.join(util_path, 'default.ini')
        os.remove(def_path)

        aux = os.path.join(util_path, '__default.ini')
        if os.path.isfile(aux):
            os.rename(aux, def_path)

    def setup(self):

        self.workbench = Workbench()
        self.workbench.register(HqcCoreManifest())
        self.workbench.register(StateManifest())
        self.workbench.register(PreferencesManifest())

    def teardown(self):
        path = os.path.join(self.test_dir, 'default_test.ini')
        if os.path.isfile(path):
            os.remove(path)
