# uncompyle6 version 3.7.0 
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: c:\Jenkins\live\output\Live\win_64_static\Release\python-bundle\MIDI Remote Scripts\MiniLab_mkII\HardwareSettingsComponent.py
# Compiled at: 2020-01-07 15:24:15
from __future__ import absolute_import, print_function, unicode_literals
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot
from _Arturia.ArturiaControlSurface import OFF_VALUE, ON_VALUE
LIVE_MEMORY_SLOT_INDEX = 7

class HardwareSettingsComponent(ControlSurfaceComponent):
    __subject_events__ = (u'live_mode', )

    def __init__(self, *a, **k):
        super(HardwareSettingsComponent, self).__init__(*a, **k)
        self._memory_slot_selection = None
        self._hardware_live_mode_switch = None
        return

    def set_memory_slot_selection(self, selection):
        self._memory_slot_selection = selection
        self._on_memory_slot_changed.subject = selection

    def set_hardware_live_mode_switch(self, switch):
        self._hardware_live_mode_switch = switch

    @subject_slot('value')
    def _on_memory_slot_changed(self, slot_data):
        slot_index = slot_data[0]
        in_live_mode = slot_index == LIVE_MEMORY_SLOT_INDEX
        self.notify_live_mode(in_live_mode)
        if self._hardware_live_mode_switch is not None:
            self._hardware_live_mode_switch.send_value((
             ON_VALUE if in_live_mode else OFF_VALUE,))
        return
# okay decompiling .\HardwareSettingsComponent.pyc
