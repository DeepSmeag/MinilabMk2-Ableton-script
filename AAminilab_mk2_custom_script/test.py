from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
import Live #you import Live, in order to be able to use its components
from _Framework.ControlSurface import ControlSurface # importthe Controle surface module
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent
from _Framework import Task
import time
import threading
from itertools import izip

from .pad_lights import *
from _Framework.Layer import Layer

from _Framework.SubjectSlot import subject_slot
from _Framework.DeviceComponent import DeviceComponent
from _Framework.SysexValueControl import SysexValueControl

from _Arturia.ArturiaControlSurface import COLOR_PROPERTY, LIVE_MODE_MSG_HEAD, LOAD_MEMORY_COMMAND, MEMORY_SLOT_PROPERTY, OFF_VALUE, SETUP_MSG_PREFIX, SETUP_MSG_SUFFIX, STORE_IN_MEMORY_COMMAND, WORKING_MEMORY_ID, WRITE_COMMAND, split_list

##from _Arturia.SessionComponent import SessionComponent
from _Arturia.MixerComponent import MixerComponent

from .HardwareSettingsComponent import HardwareSettingsComponent

##from .SessionComponent import SessionComponent

ANALOG_LAB_MEMORY_SLOT_ID = 1

LIVE_MEMORY_SLOT_ID = 8
BANKS = {(0,): 1, (1,): 2, (2,): 3, (3,): 4, (4,): 5, (5,): 6, (6,): 7, (7,): 8}
IS_MOMENTARY=True

C1 = 36
Dsharp2 = 51
pads_row2 = [0, 56, 57, 58, 59, 60, 61, 62, 63]
PAD_COLORS = [1, 16, 17, 4, 20, 5, 127, 4, 16, 4, 17, 20, 5, 127, 17, 1]
HARDWARE_ENCODER_IDS = (48, 1, 2, 9, 11, 12, 13, 14, 51, 3, 4, 10, 5, 6, 7, 8)
ENCODER_PUSH1 = 113
ENCODER_PUSH2 = 115

class test(ControlSurface):          # create a class element 
    __module__=__name__                  #name of the class
    __doc__="test function"           #documentation
    
    pad_channel = 9
    session_component_type = SessionComponent
    encoder_msg_channel = 1
    is_playing = False
    encoder_msg_ids = (22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 52, 53, 54, 55)

    IS_PRESSED_9 = False
    IS_PRESSED_10 = False
    
    
    def __init__(self, c_instance):                
        ControlSurface.__init__(self,c_instance)   #import the components of a ControlSurface
        with self.component_guard():               #don't know the use of this, but it is recquiered in live 9 scripts     
            self.show_message('Script Initiated')
            
            self._create_controls()
            
            self._create_hardware_settings()
            self._setup_transport_track()
            self._setup_controls()
            self._create_device()
            self._create_session()
            self._create_mixer()
            self._setup_messages()
            self._setup_hardware()

    def _create_controls(self):

        self._device_controls = ButtonMatrixElement(rows=[ [ EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, identifier, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Encoder_%d_%d' % (column_index, row_index)) for column_index, identifier in enumerate(row) ] for row_index, row in enumerate((self.encoder_msg_ids[:4], self.encoder_msg_ids[8:12]))
                                                         ])
        
        self._horizontal_scroll_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[7], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Horizontal_Scroll_Encoder')

##        self._vertical_scroll_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[15], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Vertical_Scroll_Encoder')
        self._master_volume_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[15], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Vertical_Scroll_Encoder')
        self._uselesss_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, 46, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Useless_Encoder')

        self._volume_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[13], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Volume_Encoder')

        self._pan_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[12], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Pan_Encoder')

        self._send_a_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[4], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Send_A_Encoder')

        self._send_b_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[5], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Send_B_Encoder')

        self._send_encoders = ButtonMatrixElement(rows=[[self._send_a_encoder, self._send_b_encoder]])

        self._return_a_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[6], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Return_A_Encoder')

        self._return_b_encoder = EncoderElement(MIDI_CC_TYPE, self.encoder_msg_channel, self.encoder_msg_ids[14], Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Return_B_Encoder')

        self._return_encoders = ButtonMatrixElement(rows=[[self._return_a_encoder, self._return_b_encoder]])

        self._encoder_push1 = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, ENCODER_PUSH1, Live.MidiMap.MapMode.absolute, name='Encoder_1')
        self._encoder_push2 = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, ENCODER_PUSH2, Live.MidiMap.MapMode.absolute, name='Encoder_2')


##        self._pad_leds = ButtonMatrixElement(rows=[[SysexValueControl(message_prefix=SETUP_MSG_PREFIX + (WRITE_COMMAND, WORKING_MEMORY_ID, COLOR_PROPERTY, column + 112), default_value=(0, ), name='Pad_LED_%d' % (column,)) for column in xrange(8) ]], name='Pad_LED_Matrix')

        self._memory_slot_selection = SysexValueControl(message_prefix=SETUP_MSG_PREFIX + (MEMORY_SLOT_PROPERTY,), name='Memory_Slot_Selection')

        self._hardware_live_mode_switch = SysexValueControl(message_prefix=LIVE_MODE_MSG_HEAD, default_value=(OFF_VALUE,), name='Hardware_Live_Mode_Switch')
    def _create_device(self):

        self._device = DeviceComponent(name='Device', is_enabled=False, layer=Layer(parameter_controls=self._device_controls), device_selection_follows_track_selection=True)

        self._device.set_enabled(False)

        self.set_device_component(self._device)    
        ##2nd Row of pads
        
##        self._light9 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[7], Live.MidiMap.MapMode.absolute, name='Pad_9')
##        self._light10 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[8], Live.MidiMap.MapMode.absolute, name='Pad_10')
##        self._pad11 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[3], Live.MidiMap.MapMode.absolute, name='Pad_11')
##        self._pad12 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[4], Live.MidiMap.MapMode.absolute, name='Pad_12')
##        self._pad13 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[5], Live.MidiMap.MapMode.absolute, name='Pad_13')
##        self._pad14 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[6], Live.MidiMap.MapMode.absolute, name='Pad_14')
##        self._pad15 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[7], Live.MidiMap.MapMode.absolute, name='Pad_15')
##        self._pad16 = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[8], Live.MidiMap.MapMode.absolute, name='Pad_16')

        

##        self._light9.add_value_listener(self._light_9, identify_sender = False)
##        self._light10.add_value_listener(self._light_10, identify_sender = False)
    def _create_session(self):

        self._session = self.session_component_type()
##        self._session.set_clip_slot_leds(self._pad_leds)
##        self._session.set_enabled(False)

    def _create_mixer(self):
        self._mixer = MixerComponent(name='Mixer', is_enabled=False, num_returns=2, layer=Layer(track_select_encoder=self._horizontal_scroll_encoder, selected_track_volume_control=self._volume_encoder, selected_track_pan_control=self._pan_encoder, selected_track_send_controls=self._send_encoders, return_volume_controls=self._return_encoders))
        self._mixer.set_enabled(False)
        
    def _create_hardware_settings(self):

        self._hardware_settings = HardwareSettingsComponent(name='Hardware_Settings', is_enabled=False, layer=Layer(memory_slot_selection=self._memory_slot_selection, hardware_live_mode_switch=self._hardware_live_mode_switch))
        self._hardware_settings.set_enabled(True)
        self._memory_slot_selection.add_value_listener(self._show_value, identify_sender = False)
##        self._on_live_mode_changed.subject = self._hardware_settings

        self._hardware_settings.set_enabled(False)
        
    @subject_slot('live_mode')
    def _on_live_mode_changed(self, is_live_mode_on):
        self._session.set_enabled(is_live_mode_on)
        
    def _show_value(self, value):
        if BANKS[value] == 8:
            #disable lights for banks 2-7
            self._turn_off_pads()
            #enable live mode
            self._turn_on_live_mode()      
        elif BANKS[value] == 1:
            #disable live mode
            self._turn_off_live_mode()
            #disable lights for banks 2-7
            self._turn_off_pads()
        else:
            #disable live mode
            self._turn_off_live_mode()
            #enable lights for banks 2-7
##            self._turn_on_pads()    
        
    def _setup_transport_track(self):
        self.transport = TransportComponent() #Instantiate a Transport Component
        self._live = Live.Application.get_application()
        self.app_instance = self._live.view
        self.song_instance = self.transport.song()
        

        self.view_instance = self.song_instance.view

        
        
        
    def _setup_controls(self):
        self._play_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[1], Live.MidiMap.MapMode.absolute, name='Play_button')
        self._stop_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[2], Live.MidiMap.MapMode.absolute, name='Stop_button')
        self._record_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[3], Live.MidiMap.MapMode.absolute, name='Record_button')
        self._overdub_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[4], Live.MidiMap.MapMode.absolute, name='Overdub_button')
        self._toggle_view_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[5], Live.MidiMap.MapMode.absolute, name='Toggle_view_button')

        self._mute_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[6], Live.MidiMap.MapMode.absolute, name='Mute_button')
        self._solo_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[7], Live.MidiMap.MapMode.absolute, name='Solo_button')
        self._arm_button = ButtonElement( IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, pads_row2[8], Live.MidiMap.MapMode.absolute, name='Arm_button')

        self._pad1 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 36, Live.MidiMap.MapMode.absolute, name='Pad_1_note')
        self._pad2 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 37, Live.MidiMap.MapMode.absolute, name='Pad_2_note')
        self._pad3 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 38, Live.MidiMap.MapMode.absolute, name='Pad_3_note')
        self._pad4 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 39, Live.MidiMap.MapMode.absolute, name='Pad_4_note')
        self._pad5 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 40, Live.MidiMap.MapMode.absolute, name='Pad_5_note')
        self._pad6 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 41, Live.MidiMap.MapMode.absolute, name='Pad_6_note')
        self._pad7 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 42, Live.MidiMap.MapMode.absolute, name='Pad_7_note')
        self._pad8 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 43, Live.MidiMap.MapMode.absolute, name='Pad_8_note')
        self._pad9 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 44, Live.MidiMap.MapMode.absolute, name='Pad_9_note')

##        self._pads = ButtonMatrixElement(rows=[[self._pad1, self._pad2, self._pad3, self._pad4, self._pad5, self._pad6, self._pad7, self._pad8]])
        
        self._pad10 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 45, Live.MidiMap.MapMode.absolute, name='Pad_10_note')
        self._pad11 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 46, Live.MidiMap.MapMode.absolute, name='Pad_11_note')
        self._pad12 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 47, Live.MidiMap.MapMode.absolute, name='Pad_12_note')
        self._pad13 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 48, Live.MidiMap.MapMode.absolute, name='Pad_13_note')
        self._pad14 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 49, Live.MidiMap.MapMode.absolute, name='Pad_14_note')
        self._pad15 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 50, Live.MidiMap.MapMode.absolute, name='Pad_15_note')
        self._pad16 = ButtonElement( IS_MOMENTARY, MIDI_NOTE_TYPE, self.pad_channel, 51, Live.MidiMap.MapMode.absolute, name='Pad_16_note')
        
        
        self._messages_to_send = []
    def _setup_messages(self):

        self._messages_to_send.append(SETUP_MSG_PREFIX + (LOAD_MEMORY_COMMAND, ANALOG_LAB_MEMORY_SLOT_ID) + SETUP_MSG_SUFFIX)


##        self.log_message(self._messages_to_send)
    def _setup_hardware(self):


        def send_subsequence(subseq):

            for msg in subseq:

##                self.log_message("MSG: ", msg)
                self._send_midi(msg)


        sequence_to_run = [ Task.run(partial(send_subsequence, subsequence)) for subsequence in split_list(self._messages_to_send, 20)]

        self._tasks.add(Task.sequence(*sequence_to_run))

        self._messages_to_send = []
    def _turn_on_live_mode(self):
        if not self.song_instance.is_playing_has_listener(self._update_leds):
            self.song_instance.add_is_playing_listener(self._update_leds)
        if not self.song_instance.record_mode_has_listener(self._update_leds):
            self.song_instance.add_record_mode_listener(self._update_leds)
        if not self.song_instance.arrangement_overdub_has_listener(self._update_leds):
            self.song_instance.add_arrangement_overdub_listener(self._update_leds)
        if not self.app_instance.focused_document_view_has_listener(self._update_leds):
            self.app_instance.add_focused_document_view_listener(self._update_leds)
        if not self.view_instance.selected_track_has_listener(self._update_leds):
            self.view_instance.add_selected_track_listener(self._update_leds)
        if not self.view_instance.selected_scene_has_listener(self._update_clips):
            self.view_instance.add_selected_scene_listener(self._update_clips)
            
        for track in self.song_instance.tracks:
            if not track.mute_has_listener(self._update_leds):
                track.add_mute_listener(self._update_leds)
            if not track.muted_via_solo_has_listener(self._update_leds):
                track.add_muted_via_solo_listener(self._update_leds)
            if not track.solo_has_listener(self._update_leds):
                track.add_solo_listener(self._update_leds)
            if not track.arm_has_listener(self._update_leds):
                track.add_arm_listener(self._update_leds)

        
        
        if not self._play_button.value_has_listener(self._play):
            self._play_button.add_value_listener(self._play, identify_sender = False)
        if not self._stop_button.value_has_listener(self._stop):
            self._stop_button.add_value_listener(self._stop, identify_sender = False)
        if not self._record_button.value_has_listener(self._record):
            self._record_button.add_value_listener(self._record, identify_sender = False)
        if not self._overdub_button.value_has_listener(self._overdub):
            self._overdub_button.add_value_listener(self._overdub, identify_sender = False)
        if not self._mute_button.value_has_listener(self._mute):
            self._mute_button.add_value_listener(self._mute, identify_sender = False)
        if not self._solo_button.value_has_listener(self._solo):
            self._solo_button.add_value_listener(self._solo, identify_sender = False)
        if not self._arm_button.value_has_listener(self._arm):
            self._arm_button.add_value_listener(self._arm, identify_sender = False)
        if not self._toggle_view_button.value_has_listener(self._toggle_view):
            self._toggle_view_button.add_value_listener(self._toggle_view, identify_sender = False)

        
        
        if not self._pad1.value_has_listener(self._clip1):
            self._pad1.add_value_listener(self._clip1, identify_sender = False)
        if not self._pad2.value_has_listener(self._clip2):
            self._pad2.add_value_listener(self._clip2, identify_sender = False)
        if not self._pad3.value_has_listener(self._clip3):
            self._pad3.add_value_listener(self._clip3, identify_sender = False)
        if not self._pad4.value_has_listener(self._clip4):
            self._pad4.add_value_listener(self._clip4, identify_sender = False)
        if not self._pad5.value_has_listener(self._clip5):
            self._pad5.add_value_listener(self._clip5, identify_sender = False)
        if not self._pad6.value_has_listener(self._clip6):
            self._pad6.add_value_listener(self._clip6, identify_sender = False)
        if not self._pad7.value_has_listener(self._clip7):
            self._pad7.add_value_listener(self._clip7, identify_sender = False)
        if not self._pad8.value_has_listener(self._clip8):
            self._pad8.add_value_listener(self._clip8, identify_sender = False)

        self._update_leds()
        
        self._device.set_enabled(True)
        self._session.set_enabled(True)
        self._mixer.set_enabled(True)
        self._mixer.master_strip().set_volume_control(self._master_volume_encoder)
    def _turn_off_live_mode(self):
        for pad in range(0,16):
            self._turn_led_off(pad)
        if self.song_instance.is_playing_has_listener(self._update_leds):
            self.song_instance.remove_is_playing_listener(self._update_leds)
        if self.song_instance.record_mode_has_listener(self._update_leds):
            self.song_instance.remove_record_mode_listener(self._update_leds)
        if self.song_instance.arrangement_overdub_has_listener(self._update_leds):
            self.song_instance.remove_arrangement_overdub_listener(self._update_leds)
        if self.app_instance.focused_document_view_has_listener(self._update_leds):
            self.app_instance.remove_focused_document_view_listener(self._update_leds)
        if self.view_instance.selected_track_has_listener(self._update_leds):
            self.view_instance.remove_selected_track_listener(self._update_leds)
        if self.view_instance.selected_scene_has_listener(self._update_clips):
            self.view_instance.remove_selected_scene_listener(self._update_clips)
            
        for track in self.song_instance.tracks:
            if track.arm_has_listener(self._update_leds):
                track.remove_arm_listener(self._update_leds)
            if track.mute_has_listener(self._update_leds):
                track.remove_mute_listener(self._update_leds)
            if track.muted_via_solo_has_listener(self._update_leds):
                track.remove_muted_via_solo_listener(self._update_leds)
            if track.solo_has_listener(self._update_leds):
                track.remove_solo_listener(self._update_leds)
            
        if self._play_button.value_has_listener(self._play):
            self._play_button.remove_value_listener(self._play)
        if self._stop_button.value_has_listener(self._stop):
            self._stop_button.remove_value_listener(self._stop)
        if self._record_button.value_has_listener(self._record):
            self._record_button.remove_value_listener(self._record)
        if self._overdub_button.value_has_listener(self._overdub):
            self._overdub_button.remove_value_listener(self._overdub)
        if self._mute_button.value_has_listener(self._mute):
            self._mute_button.remove_value_listener(self._mute)
        if self._solo_button.value_has_listener(self._solo):
            self._solo_button.remove_value_listener(self._solo)
        if self._arm_button.value_has_listener(self._arm):
            self._arm_button.remove_value_listener(self._arm)
        if self._toggle_view_button.value_has_listener(self._toggle_view):
            self._toggle_view_button.remove_value_listener(self._toggle_view)
            

        if self._pad1.value_has_listener(self._clip1):
            self._pad1.remove_value_listener(self._clip1)
        if self._pad2.value_has_listener(self._clip2):
            self._pad2.remove_value_listener(self._clip2)
        if self._pad3.value_has_listener(self._clip3):
            self._pad3.remove_value_listener(self._clip3)
        if self._pad4.value_has_listener(self._clip4):
            self._pad4.remove_value_listener(self._clip4)
        if self._pad5.value_has_listener(self._clip5):
            self._pad5.remove_value_listener(self._clip5)
        if self._pad6.value_has_listener(self._clip6):
            self._pad6.remove_value_listener(self._clip6)
        if self._pad7.value_has_listener(self._clip7):
            self._pad7.remove_value_listener(self._clip7)
        if self._pad8.value_has_listener(self._clip8):
            self._pad8.remove_value_listener(self._clip8)
        

        self._device.set_enabled(False)
        self._session.set_enabled(False)
        self._mixer.master_strip().set_volume_control(self._uselesss_encoder)
        self._mixer.set_enabled(False)
    def _update_leds(self):
        update_c_leds = threading.Thread(target = self._update_clip_leds, args=())
        update_c_leds.daemon = True
        update_c_leds.start()
        if self.song_instance.is_playing:
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 4, 247))
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 1, 247))
        else:
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 5, 247))
            if self.song_instance.current_song_time > 0:
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 5, 247))
            else:
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 127, 247))
        if self.song_instance.record_mode:
            #Change led
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 10 , 1, 247))
        else:
            #change led
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 10 , 20, 247))
        if self.song_instance.arrangement_overdub:
            #update led
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 11 , 5, 247)) #yellow when overdubbing
        else:
            #update led
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 11 , 16, 247)) #blue when not overdubbing
        if self.view_instance.selected_track.arm:
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15 , 1, 247)) #red when armed
        else:
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15 , 4, 247)) #green when not armed
        if self.view_instance.selected_track.muted_via_solo:
            if self.view_instance.selected_track.mute:
                #led blue
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 16, 247))
            else:
                #led cyan
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 20, 247))
        else:
            if self.view_instance.selected_track.mute:
                #led red
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 1, 247))
            else:
                #led green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 4, 247))
        if self.view_instance.selected_track.solo:
            #led blue
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 14 , 16, 247))
        else:
            #led purple
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 14 , 127, 247))
        if self.app_instance.focused_document_view == "Arranger":
            #clear prev mappings
            self._session._on_next_scene_value.subject = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, 114, Live.MidiMap.MapMode.absolute, name='Encoder_1')
            self._session._on_prev_scene_value.subject = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, self.pad_channel, 116, Live.MidiMap.MapMode.absolute, name='Encoder_1')
            #new mappings
            self._encoder_push1.add_value_listener(self._previous_track, identify_sender = False)
            self._encoder_push2.add_value_listener(self._next_track, identify_sender = False)
            
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 12 , 20, 247))
        else:
            #clear prev mappings
            self._encoder_push1.remove_value_listener(self._previous_track)
            self._encoder_push2.remove_value_listener(self._next_track)
            self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 12 , 17, 247))
            #new mappings
            self._session._on_next_scene_value.subject = self._encoder_push2
            self._session._on_prev_scene_value.subject = self._encoder_push1
            
           
    def _play(self, value):
        if value>0:
            if self.song_instance.is_playing:
                #pause the song
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 5, 247))
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 127, 247))
                self.song_instance.stop_playing()
            else:
                self.song_instance.start_playing()
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 4, 247))
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 1, 247))
        else:
            self._update_leds()
    def _stop(self, value):
        if value>0:
            if self.song_instance.is_playing:
                #stop the song
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 1, 247)) #red - press red to stop
                self.song_instance.stop_playing()
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 5, 247)) #pad 9 turns yellow because of stop
            else:
                self.song_instance.stop_playing()
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 127, 247)) #white - press to go to beginning
        else:
            self._update_leds()
    
    def _record(self, value):
        if value>0:
            if self.song_instance.record_mode:
                #stop recording
                self.song_instance.record_mode = False
                #Change led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 10 , 0, 247))
            else:
                #record
                self.song_instance.record_mode = True
                #change led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 10 , 20, 247))
        else:
            self._update_leds()
    def _overdub(self, value):
        if value>0:
            if self.song_instance.arrangement_overdub:
                #turn off overdub
                self.song_instance.arrangement_overdub = False
                #update led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 11 , 16, 247)) #blue when not overdubbing
            else:
                #turn on overdub
                self.song_instance.arrangement_overdub = True
                #update led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 11 , 5, 247)) #yellow when overdubbing
        else:
            self._update_leds()
    def _mute(self, value):
        if value>0:
            if self.view_instance.selected_track.muted_via_solo:
                if self.view_instance.selected_track.mute:
                    #unmute
                    self.view_instance.selected_track.mute = False
                    #led cyan
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 20, 247))
                else:
                    #mute
                    self.view_instance.selected_track.mute = True
                    #led blue
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 16, 247))
            else:
                if self.view_instance.selected_track.mute:
                    #unmute
                    self.view_instance.selected_track.mute = False
                    #led green
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 4, 247))
                else:
                    #mute
                    self.view_instance.selected_track.mute = True
                    #led red
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 1, 247))    
        else:
            self._update_leds()
    def _solo(self, value):
        if value>0:
            if self.view_instance.selected_track.solo:
                #unsolo
                self.view_instance.selected_track.solo = False
                #led purple
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 14 , 127, 247))
            else:
                #solo
                self.view_instance.selected_track.solo = True
                #led red
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 14 , 16, 247))    
        else:
            self._update_leds()
    def _arm(self, value):
        if value>0:
            if self.view_instance.selected_track.can_be_armed:
                if self.view_instance.selected_track.arm == False:
                    #arm track
                    self.view_instance.selected_track.arm = True
                    #update led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15 , 1, 247))
                else:
                    #disarm track
                    self.view_instance.selected_track.arm = False
                    #update led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15 , 4, 247))
        else:
            self._update_leds()
    def _previous_track(self, value):
        if value>0:
            self._mixer._select_prev_track()
    def _next_track(self, value):
        if value>0:
            self._mixer._select_next_track()

    def _toggle_view(self, value):
        if value>0:
            if self.app_instance.focused_document_view == "Arranger":
                #change tab to Session
                self.app_instance.focus_view("Session")
                #led purple
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 12 , 17, 247)) 
            else:
                #change tab to Arranger
                self.app_instance.focus_view("Arranger")
                #led cyan
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 12 , 20, 247))
        else:
            self._update_leds()
    
    def _light_show_1(self):
        while self.IS_PRESSED_9:
            for pad in range(8,16):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad -1, 0, 247))
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
                time.sleep(0.07)      #############################Speed when going right (lower - faster)
            for pad in range(14,7,-1):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad +1, 0, 247))
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
                time.sleep(.05)       #############################Speed when going left (lower - faster)
        ###########STOPPING WHEN BUTTON IS PRESSED AGAIN###################
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 8 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 9 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 10 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 11 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 12 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 13 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 14 , 0, 247))
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15 , 0, 247))
    def _light_show_2(self):
        while self.IS_PRESSED_10:
            for pad in range(8,16):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
                time.sleep(0.05)
            for pad in range(8,16):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad, 0, 247))
                time.sleep(0.05)
            for pad in range(15,7,-1):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad, PAD_COLORS[pad], 247))
                time.sleep(.05)
            for pad in range(15,7,-1):
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad, 0, 247))
                time.sleep(.05)
    def _turn_led_on(self, pad):
##        self.log_message('TURN LED ON CALLED=====================')
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
    def _turn_led_off(self, pad):
##        self.log_message('TURN LED OFF CALLED//////////////////////////////////////////')
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad, 0, 247))



    def disconnect(self):              #this function is automatically called by live when the program is closed
        for pad in range(0,16):
            self._turn_led_off(pad)
        if self.song_instance.is_playing_has_listener(self._update_leds):
            self.song_instance.remove_is_playing_listener(self._update_leds)
        if self.song_instance.record_mode_has_listener(self._update_leds):
            self.song_instance.remove_record_mode_listener(self._update_leds)
        if self.song_instance.arrangement_overdub_has_listener(self._update_leds):
            self.song_instance.remove_arrangement_overdub_listener(self._update_leds)
        if self.view_instance.selected_track_has_listener(self._update_leds):
            self.view_instance.remove_selected_track_listener(self._update_leds)
        for track in self.song_instance.tracks:
            if track.arm_has_listener(self._update_leds):
                track.remove_arm_listener(self._update_leds)
            if track.mute_has_listener(self._update_leds):
                track.remove_mute_listener(self._update_leds)
            if track.muted_via_solo_has_listener(self._update_leds):
                track.remove_muted_via_solo_listener(self._update_leds)
            if track.solo_has_listener(self._update_leds):
                track.remove_solo_listener(self._update_leds)
        if self._play_button.value_has_listener(self._play):
            self._play_button.remove_value_listener(self._play)
        if self._stop_button.value_has_listener(self._stop):
            self._stop_button.remove_value_listener(self._stop)
        if self._record_button.value_has_listener(self._record):
            self._record_button.remove_value_listener(self._record)
        if self._overdub_button.value_has_listener(self._overdub):
            self._overdub_button.remove_value_listener(self._overdub)
        if self._mute_button.value_has_listener(self._mute):
            self._mute_button.remove_value_listener(self._mute)
        if self._solo_button.value_has_listener(self._solo):
            self._solo_button.remove_value_listener(self._solo)
        if self._arm_button.value_has_listener(self._arm):
            self._arm_button.remove_value_listener(self._arm)
        if self._toggle_view_button.value_has_listener(self._toggle_view):
            self._toggle_view_button.remove_value_listener(self._toggle_view)
        if self.app_instance.focused_document_view_has_listener(self._update_leds):
            self.app_instance.remove_focused_document_view_listener(self._update_leds)
        if self.view_instance.selected_scene_has_listener(self._update_clips):
            self.view_instance.remove_selected_scene_listener(self._update_clips)
            
        self._memory_slot_selection.remove_value_listener(self._show_value)


        if self._pad1.value_has_listener(self._pad_pressed_1):
            self._pad1.remove_value_listener(self._pad_pressed_1)
        if self._pad2.value_has_listener(self._pad_pressed_2):
            self._pad2.remove_value_listener(self._pad_pressed_2)
        if self._pad3.value_has_listener(self._pad_pressed_3):
            self._pad3.remove_value_listener(self._pad_pressed_3)
        if self._pad4.value_has_listener(self._pad_pressed_4):
            self._pad4.remove_value_listener(self._pad_pressed_4)
        if self._pad5.value_has_listener(self._pad_pressed_5):
            self._pad5.remove_value_listener(self._pad_pressed_5)
        if self._pad6.value_has_listener(self._pad_pressed_6):
            self._pad6.remove_value_listener(self._pad_pressed_6)
        if self._pad7.value_has_listener(self._pad_pressed_7):
            self._pad7.remove_value_listener(self._pad_pressed_7)
        if self._pad8.value_has_listener(self._pad_pressed_8):
            self._pad8.remove_value_listener(self._pad_pressed_8)
        if self._pad9.value_has_listener(self._pad_pressed_9):
            self._pad9.remove_value_listener(self._pad_pressed_9)
        if self._pad10.value_has_listener(self._pad_pressed_10):
            self._pad10.remove_value_listener(self._pad_pressed_10)
        if self._pad11.value_has_listener(self._pad_pressed_11):
            self._pad11.remove_value_listener(self._pad_pressed_11)
        if self._pad12.value_has_listener(self._pad_pressed_12):
            self._pad12.remove_value_listener(self._pad_pressed_12)
        if self._pad13.value_has_listener(self._pad_pressed_13):
            self._pad13.remove_value_listener(self._pad_pressed_13)
        if self._pad14.value_has_listener(self._pad_pressed_14):
            self._pad14.remove_value_listener(self._pad_pressed_14)
        if self._pad15.value_has_listener(self._pad_pressed_15):
            self._pad15.remove_value_listener(self._pad_pressed_15)
        if self._pad16.value_has_listener(self._pad_pressed_16):
            self._pad16.remove_value_listener(self._pad_pressed_16)

        for scene in self.song_instance.scenes:
            for clip in scene.clip_slots:
                if clip.playing_status_has_listener(self._update_clip_leds):
                    clip.remove_playing_status_listener(self._update_clip_leds)
                if clip.has_clip_has_listener(self._update_clip_leds):
                    clip.remove_has_clip_listener(self._update_clip_leds)

        
    def _turn_on_pads(self):
        
        if not self._pad1.pad_pressed_has_listener(self._pad_pressed_1):
            self._pad1.add_pad_pressed_listener(self._pad_pressed_1, identify_sender = False)
            self._pad1.use_default_message()
##            self._pad1.force_next_send()
##            self.log_message(self._pad1.mapped_parameter)
        if not self._pad2.value_has_listener(self._pad_pressed_2):
            self._pad2.add_value_listener(self._pad_pressed_2, identify_sender = False)
        if not self._pad3.value_has_listener(self._pad_pressed_3):
            self._pad3.add_value_listener(self._pad_pressed_3, identify_sender = False)
        if not self._pad4.value_has_listener(self._pad_pressed_4):
            self._pad4.add_value_listener(self._pad_pressed_4, identify_sender = False)
        if not self._pad5.value_has_listener(self._pad_pressed_5):
            self._pad5.add_value_listener(self._pad_pressed_5, identify_sender = False)
        if not self._pad6.value_has_listener(self._pad_pressed_6):
            self._pad6.add_value_listener(self._pad_pressed_6, identify_sender = False)
        if not self._pad7.value_has_listener(self._pad_pressed_7):
            self._pad7.add_value_listener(self._pad_pressed_7, identify_sender = False)
        if not self._pad8.value_has_listener(self._pad_pressed_8):
            self._pad8.add_value_listener(self._pad_pressed_8, identify_sender = False)
        if not self._pad9.value_has_listener(self._pad_pressed_9):
            self._pad9.add_value_listener(self._pad_pressed_9, identify_sender = False)
        if not self._pad10.value_has_listener(self._pad_pressed_10):
            self._pad10.add_value_listener(self._pad_pressed_10, identify_sender = False)
        if not self._pad11.value_has_listener(self._pad_pressed_11):
            self._pad11.add_value_listener(self._pad_pressed_11, identify_sender = False)
        if not self._pad12.value_has_listener(self._pad_pressed_12):
            self._pad12.add_value_listener(self._pad_pressed_12, identify_sender = False)
        if not self._pad13.value_has_listener(self._pad_pressed_13):
            self._pad13.add_value_listener(self._pad_pressed_13, identify_sender = False)
        if not self._pad14.value_has_listener(self._pad_pressed_14):
            self._pad14.add_value_listener(self._pad_pressed_14, identify_sender = False)
        if not self._pad15.value_has_listener(self._pad_pressed_15):
            self._pad15.add_value_listener(self._pad_pressed_15, identify_sender = False)
        if not self._pad16.value_has_listener(self._pad_pressed_16):
            self._pad16.add_value_listener(self._pad_pressed_16, identify_sender = False)
        
    def _turn_off_pads(self):       
        if self._pad1.value_has_listener(self._pad_pressed_1):
            self._pad1.remove_value_listener(self._pad_pressed_1)
        if self._pad2.value_has_listener(self._pad_pressed_2):
            self._pad2.remove_value_listener(self._pad_pressed_2)
        if self._pad3.value_has_listener(self._pad_pressed_3):
            self._pad3.remove_value_listener(self._pad_pressed_3)
        if self._pad4.value_has_listener(self._pad_pressed_4):
            self._pad4.remove_value_listener(self._pad_pressed_4)
        if self._pad5.value_has_listener(self._pad_pressed_5):
            self._pad5.remove_value_listener(self._pad_pressed_5)
        if self._pad6.value_has_listener(self._pad_pressed_6):
            self._pad6.remove_value_listener(self._pad_pressed_6)
        if self._pad7.value_has_listener(self._pad_pressed_7):
            self._pad7.remove_value_listener(self._pad_pressed_7)
        if self._pad8.value_has_listener(self._pad_pressed_8):
            self._pad8.remove_value_listener(self._pad_pressed_8)
        if self._pad9.value_has_listener(self._pad_pressed_9):
            self._pad9.remove_value_listener(self._pad_pressed_9)
        if self._pad10.value_has_listener(self._pad_pressed_10):
            self._pad10.remove_value_listener(self._pad_pressed_10)
        if self._pad11.value_has_listener(self._pad_pressed_11):
            self._pad11.remove_value_listener(self._pad_pressed_11)
        if self._pad12.value_has_listener(self._pad_pressed_12):
            self._pad12.remove_value_listener(self._pad_pressed_12)
        if self._pad13.value_has_listener(self._pad_pressed_13):
            self._pad13.remove_value_listener(self._pad_pressed_13)
        if self._pad14.value_has_listener(self._pad_pressed_14):
            self._pad14.remove_value_listener(self._pad_pressed_14)
        if self._pad15.value_has_listener(self._pad_pressed_15):
            self._pad15.remove_value_listener(self._pad_pressed_15)
        if self._pad16.value_has_listener(self._pad_pressed_16):
            self._pad16.remove_value_listener(self._pad_pressed_16)
    def _light_9(self, value):
        self.show_message('Pad 9 pressed')
        if value>0:
            self.IS_PRESSED_9 = not self.IS_PRESSED_9
            if self.IS_PRESSED_9:
                light_9 = threading.Thread(target = self._light_show_1, args=())
                light_9.daemon = True
                light_9.start()   
        else:
            self.show_message("Pad 9 unpressed")

    def _light_10(self, value):
        self.show_message('Pad 10 pressed')
        if value>0:
            self.IS_PRESSED_10 = not self.IS_PRESSED_10
            if self.IS_PRESSED_10:
                light_10 = threading.Thread(target = self._light_show_2, args=())
                light_10.daemon = True
                light_10.start()
        else:
            self.show_message('Pad 10 unpressed')

    @subject_slot('pad_pressed')    
    def _pad_pressed_1(self, value):
        
        if value > 0:
##            self._pad1.force_next_send()
            self.log_message(self._pad1._mapping_feedback_values())
##            self._pad_pressed_1.subject = None
##            self._pad1._suppress_script_forwarding = not self._pad1._suppress_script_forwarding
##            self._send_midi((144+self.pad_channel, 36, value))
##            self._pad1._do_send_value(value, channel = self.pad_channel)
##            self._pad1._do_send_value(value, channel = self.pad_channel)
            self.show_message('Pad 1 pressed')
            pad1_asc = threading.Thread(target = light_pads_asc, args=(self, 0,))
            pad1_desc = threading.Thread(target = light_pads_desc, args=(self, 0,))
            pad1_asc.daemon = True
            pad1_desc.daemon = True
            pad1_asc.start()
            pad1_desc.start()
            self._pad1._suppress_script_forwarding = not self._pad1._suppress_script_forwarding
            self._do_receive_midi((144+self.pad_channel, 36, value))
            self._pad1._suppress_script_forwarding = not self._pad1._suppress_script_forwarding
        else:
            
##            self._pad_pressed_1.subject = self._pad1
##            self._pad1._suppress_script_forwarding = not self._pad1._suppress_script_forwarding
##            self._pad1.force_next_send()
            self.show_message('Pad 1 unpressed')
    def _pad_pressed_2(self, value):
        self.show_message('Pad 2 pressed')
        if value > 0:
            pad2_asc = threading.Thread(target = light_pads_asc, args=(self, 1,))
            pad2_desc = threading.Thread(target = light_pads_desc, args=(self, 1,))
            pad2_asc.daemon = True
            pad2_desc.daemon = True
            pad2_asc.start()
            pad2_desc.start()
        else:
            self.show_message('Pad 2 unpressed')
    def _pad_pressed_3(self, value):
        self.show_message('Pad 3 pressed')
        if value > 0:
            pad3_asc = threading.Thread(target = light_pads_asc, args=(self, 2,))
            pad3_desc = threading.Thread(target = light_pads_desc, args=(self, 2,))
            pad3_asc.daemon = True
            pad3_desc.daemon = True
            pad3_asc.start()
            pad3_desc.start()
        else:
            self.show_message('Pad 3 unpressed')
    def _pad_pressed_4(self, value):
        self.show_message('Pad 4 pressed')
        if value > 0:
            pad4_asc = threading.Thread(target = light_pads_asc, args=(self, 3,))
            pad4_desc = threading.Thread(target = light_pads_desc, args=(self, 3,))
            pad4_asc.daemon = True
            pad4_desc.daemon = True
            pad4_asc.start()
            pad4_desc.start()
        else:
            self.show_message('Pad 4 unpressed')
    def _pad_pressed_5(self, value):
        self.show_message('Pad 5 pressed')
        if value > 0:
            pad5_asc = threading.Thread(target = light_pads_asc, args=(self, 4,))
            pad5_desc = threading.Thread(target = light_pads_desc, args=(self, 4,))
            pad5_asc.daemon = True
            pad5_desc.daemon = True
            pad5_asc.start()
            pad5_desc.start()
        else:
            self.show_message('Pad 5 unpressed')
    def _pad_pressed_6(self, value):
        self.show_message('Pad 6 pressed')
        if value > 0:
            pad6_asc = threading.Thread(target = light_pads_asc, args=(self, 5,))
            pad6_desc = threading.Thread(target = light_pads_desc, args=(self, 5,))
            pad6_asc.daemon = True
            pad6_desc.daemon = True
            pad6_asc.start()
            pad6_desc.start()
        else:
            self.show_message('Pad 6 unpressed')
    def _pad_pressed_7(self, value):
        self.show_message('Pad 7 pressed')
        if value > 0:
            pad7_asc = threading.Thread(target = light_pads_asc, args=(self, 6,))
            pad7_desc = threading.Thread(target = light_pads_desc, args=(self, 6,))
            pad7_asc.daemon = True
            pad7_desc.daemon = True
            pad7_asc.start()
            pad7_desc.start()
        else:
            self.show_message('Pad 7 unpressed')
    def _pad_pressed_8(self, value):
        self.show_message('Pad 8 pressed')
        if value > 0:
            pad8_asc = threading.Thread(target = light_pads_asc, args=(self, 7,))
            pad8_desc = threading.Thread(target = light_pads_desc, args=(self, 7,))
            pad8_asc.daemon = True
            pad8_desc.daemon = True
            pad8_asc.start()
            pad8_desc.start()
        else:
            self.show_message('Pad 8 unpressed')
    def _pad_pressed_9(self, value):
        self.show_message('Pad 9 pressed')
        if value > 0:
            pad9_asc = threading.Thread(target = light_pads_asc, args=(self, 8,))
            pad9_desc = threading.Thread(target = light_pads_desc, args=(self, 8,))
            pad9_asc.daemon = True
            pad9_desc.daemon = True
            pad9_asc.start()
            pad9_desc.start()
        else:
            self.show_message('Pad 9 unpressed')
    def _pad_pressed_10(self, value):
        self.show_message('Pad 10 pressed')
        if value > 0:
            pad10_asc = threading.Thread(target = light_pads_asc, args=(self, 9,))
            pad10_desc = threading.Thread(target = light_pads_desc, args=(self, 9,))
            pad10_asc.daemon = True
            pad10_desc.daemon = True
            pad10_asc.start()
            pad10_desc.start()
        else:
            self.show_message('Pad 10 unpressed')
    def _pad_pressed_11(self, value):
        self.show_message('Pad 11 pressed')
        if value > 0:
            pad11_asc = threading.Thread(target = light_pads_asc, args=(self, 10,))
            pad11_desc = threading.Thread(target = light_pads_desc, args=(self, 10,))
            pad11_asc.daemon = True
            pad11_desc.daemon = True
            pad11_asc.start()
            pad11_desc.start()
        else:
            self.show_message('Pad 11 unpressed')
    def _pad_pressed_12(self, value):
        self.show_message('Pad 12 pressed')
        if value > 0:
            pad12_asc = threading.Thread(target = light_pads_asc, args=(self, 11,))
            pad12_desc = threading.Thread(target = light_pads_desc, args=(self, 11,))
            pad12_asc.daemon = True
            pad12_desc.daemon = True
            pad12_asc.start()
            pad12_desc.start()
        else:
            self.show_message('Pad 12 unpressed')
    def _pad_pressed_13(self, value):
        self.show_message('Pad 13 pressed')
        if value > 0:
            pad13_asc = threading.Thread(target = light_pads_asc, args=(self, 12,))
            pad13_desc = threading.Thread(target = light_pads_desc, args=(self, 12,))
            pad13_asc.daemon = True
            pad13_desc.daemon = True
            pad13_asc.start()
            pad13_desc.start()
        else:
            self.show_message('Pad 13 unpressed')
    def _pad_pressed_14(self, value):
        self.show_message('Pad 14 pressed')
        if value > 0:
            pad14_asc = threading.Thread(target = light_pads_asc, args=(self, 13,))
            pad14_desc = threading.Thread(target = light_pads_desc, args=(self, 13,))
            pad14_asc.daemon = True
            pad14_desc.daemon = True
            pad14_asc.start()
            pad14_desc.start()
        else:
            self.show_message('Pad 14 unpressed')
    def _pad_pressed_15(self, value):
        self.show_message('Pad 15 pressed')
        if value > 0:
            pad15_asc = threading.Thread(target = light_pads_asc, args=(self, 14,))
            pad15_desc = threading.Thread(target = light_pads_desc, args=(self, 14,))
            pad15_asc.daemon = True
            pad15_desc.daemon = True
            pad15_asc.start()
            pad15_desc.start()
        else:
            self.show_message('Pad 15 unpressed')
    def _pad_pressed_16(self, value):
        self.show_message('Pad 16 pressed')
        if value > 0:
            pad16_asc = threading.Thread(target = light_pads_asc, args=(self, 15,))
            pad16_desc = threading.Thread(target = light_pads_desc, args=(self, 15,))
            pad16_asc.daemon = True
            pad16_desc.daemon = True
            pad16_asc.start()
            pad16_desc.start()
        else:
            self.show_message('Pad 16 unpressed')
    def _update_clip_leds(self):
        for clip in xrange(0, len(self.song_instance.tracks)):
            if self.view_instance.selected_scene.clip_slots[clip].has_clip:
                if not self.view_instance.selected_scene.clip_slots[clip].is_triggered and not self.view_instance.selected_scene.clip_slots[clip].is_playing:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 5, 247))     # yellow if on standby
##                    self.show_message("Supposed to be on standby and have clip")
                elif self.view_instance.selected_scene.clip_slots[clip].is_playing and not self.view_instance.selected_scene.clip_slots[clip].is_recording:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 4, 247))     # green
##                    self.show_message("Supposed to be green with clip")
                elif self.view_instance.selected_scene.clip_slots[clip].is_recording:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 1, 247))     # red
##                    self.show_message("Supposed to be recording")
                elif self.view_instance.selected_scene.clip_slots[clip].is_triggered:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 20, 247))     # cyan   
##                    self.show_message("Supposed to be temporary cyan")
            else:
##                if self.view_instance.selected_scene.clip_slots[clip].will_record_on_start:
                
                if self.view_instance.selected_scene.clip_slots[clip].is_triggered:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 20, 247))     # cyan
##                    self.show_message("Triggered with no clip")
                elif self.view_instance.selected_scene.clip_slots[clip].canonical_parent.arm:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 17, 247))    # magenta
##                    self.show_message("Can record but not triggered")
                else:
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + clip , 0, 247)) #off if no clip in clipslot and not gonna record
    def _update_clips(self):
        for clip in self.view_instance.selected_scene.clip_slots:
            if not clip.playing_status_has_listener(self._update_clip_leds):
                clip.add_playing_status_listener(self._update_clip_leds)
            if not clip.has_clip_has_listener(self._update_clip_leds):
                clip.add_has_clip_listener(self._update_clip_leds)
        self._update_clip_leds()    
    def _check_clip_leds(self):
        for x in xrange(10):
            
            self._update_clip_leds()
            time.sleep(0.2)
        
    def _clip1(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[0].is_playing:
                if self.view_instance.selected_scene.clip_slots[0].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 0 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 0 , 20, 247))
                self.view_instance.selected_scene.clip_slots[0].fire()
                
            elif self.view_instance.selected_scene.clip_slots[0].is_recording:
                self.view_instance.selected_scene.clip_slots[0].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 0 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 0 , 4, 247))
                self.view_instance.selected_scene.clip_slots[0].stop()
        else:
            clip1_check = threading.Thread(target = self._check_clip_leds, args=())
            clip1_check.daemon = True
            clip1_check.start()
            
    def _clip2(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[1].is_playing:
                if self.view_instance.selected_scene.clip_slots[1].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 1 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 1 , 20, 247))
                self.view_instance.selected_scene.clip_slots[1].fire()
                
            elif self.view_instance.selected_scene.clip_slots[1].is_recording:
                self.view_instance.selected_scene.clip_slots[1].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 1 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 1 , 4, 247))
                self.view_instance.selected_scene.clip_slots[1].stop()
        else:
            clip2_check = threading.Thread(target = self._check_clip_leds, args=())
            clip2_check.daemon = True
            clip2_check.start()
    def _clip3(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[2].is_playing:
                if self.view_instance.selected_scene.clip_slots[2].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 2 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 2 , 20, 247))
                self.view_instance.selected_scene.clip_slots[2].fire()
                
            elif self.view_instance.selected_scene.clip_slots[2].is_recording:
                self.view_instance.selected_scene.clip_slots[2].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 2 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 2 , 4, 247))
                self.view_instance.selected_scene.clip_slots[2].stop()
        else:
            clip3_check = threading.Thread(target = self._check_clip_leds, args=())
            clip3_check.daemon = True
            clip3_check.start()
    def _clip4(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[3].is_playing:
                if self.view_instance.selected_scene.clip_slots[3].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 3 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 3 , 20, 247))
                self.view_instance.selected_scene.clip_slots[3].fire()
                
            elif self.view_instance.selected_scene.clip_slots[3].is_recording:
                self.view_instance.selected_scene.clip_slots[3].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 3 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 3 , 4, 247))
                self.view_instance.selected_scene.clip_slots[3].stop()
        else:
            clip4_check = threading.Thread(target = self._check_clip_leds, args=())
            clip4_check.daemon = True
            clip4_check.start()
    def _clip5(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[4].is_playing:
                if self.view_instance.selected_scene.clip_slots[4].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 4 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 4 , 20, 247))
                self.view_instance.selected_scene.clip_slots[4].fire()
                
            elif self.view_instance.selected_scene.clip_slots[4].is_recording:
                self.view_instance.selected_scene.clip_slots[4].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 4 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 4 , 4, 247))
                self.view_instance.selected_scene.clip_slots[4].stop()
        else:
            clip5_check = threading.Thread(target = self._check_clip_leds, args=())
            clip5_check.daemon = True
            clip5_check.start()
    def _clip6(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[5].is_playing:
                if self.view_instance.selected_scene.clip_slots[5].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 5 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 5 , 20, 247))
                self.view_instance.selected_scene.clip_slots[5].fire()
                
            elif self.view_instance.selected_scene.clip_slots[5].is_recording:
                self.view_instance.selected_scene.clip_slots[5].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 5 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 5 , 4, 247))
                self.view_instance.selected_scene.clip_slots[5].stop()
        else:
            clip6_check = threading.Thread(target = self._check_clip_leds, args=())
            clip6_check.daemon = True
            clip6_check.start()
    def _clip7(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[6].is_playing:
                if self.view_instance.selected_scene.clip_slots[6].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 6 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 6 , 20, 247))
                self.view_instance.selected_scene.clip_slots[6].fire()
                
            elif self.view_instance.selected_scene.clip_slots[6].is_recording:
                self.view_instance.selected_scene.clip_slots[6].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 6 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 6 , 4, 247))
                self.view_instance.selected_scene.clip_slots[6].stop()
        else:
            clip7_check = threading.Thread(target = self._check_clip_leds, args=())
            clip7_check.daemon = True
            clip7_check.start()
    def _clip8(self, value):
        if value>0:
            if not self.view_instance.selected_scene.clip_slots[7].is_playing:
                if self.view_instance.selected_scene.clip_slots[7].will_record_on_start:
                    #red led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 7 , 1, 247))
                else:
                    # cyan led
                    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 11270 , 20, 247))
                self.view_instance.selected_scene.clip_slots[7].fire()
                
            elif self.view_instance.selected_scene.clip_slots[7].is_recording:
                self.view_instance.selected_scene.clip_slots[7].fire()
                # red led
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 7 , 1, 247))
            else:
                #green
                self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 7 , 4, 247))
                self.view_instance.selected_scene.clip_slots[7].stop()
        else:
            clip8_check = threading.Thread(target = self._check_clip_leds, args=())
            clip8_check.daemon = True
            clip8_check.start()
