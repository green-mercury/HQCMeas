# -*- coding: utf-8 -*-
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

import os

from traits.api import (Str, HasTraits, Instance, Button, Any,
                        on_trait_change)
from traitsui.api import View, UItem, HGroup, VGroup
from measurement.measurement_editor import MeasurementEditor
from measurement.measurement_execution import TaskExecutionControl
from pprint import pprint
import sys

class StdoutRedirection(HasTraits):

    string = Str('')
    out = Any

    def write(self, mess):
        mess.rstrip()
        self.string += mess

        if self.out:
            self.out.write(mess + '\n')

class Test(HasTraits):
    editor = Instance(MeasurementEditor)
    exe_control = Instance(TaskExecutionControl)
    out = Instance(StdoutRedirection)
    button2 = Button('Print database')

    view = View(
                VGroup(
                    HGroup(
                        UItem('editor@'),
                        UItem('exe_control@', width = -300),
                        ),
                    UItem('button2'),
                ),
                resizable = True,
                )

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
#        self.out = StdoutRedirection(out = sys.stdout)
#        sys.stdout = self.out

    @on_trait_change('editor:enqueue_button')
    def enqueue_measurement(self):
        if self.editor.root_task.check():
            self.exe_control.append_task(self.editor.root_task)
            self.editor.new_root_task()

    def _button2_changed(self):
        pprint(self.editor.root_task.task_database._database)

if __name__ == '__main__':
    editor = MeasurementEditor()
    editor.new_root_task()

    Test(editor = editor, exe_control = TaskExecutionControl()).configure_traits()
