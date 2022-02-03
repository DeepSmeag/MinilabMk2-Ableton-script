from __future__ import absolute_import, print_function, unicode_literals
import Live
from time import sleep
PAD_COLORS = [1, 16, 17, 4, 20, 5, 127, 4, 16, 4, 17, 20, 5, 127, 17, 1]
##Pads are from C1 to D#2, corresponding midi notes from 36 to 51 included

pad_channel = 9

def light_pads_asc(self, starting_pad):
    for pad in range(starting_pad + 1, 16):
        
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
        sleep(.05)
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad -1, 0, 247))
    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + 15, 0, 247))
def light_pads_desc(self, starting_pad):    
    for pad in range(starting_pad - 1, -1, -1):
        
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad , PAD_COLORS[pad], 247))
        sleep(.05)
        self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112 + pad +1, 0, 247))
    self._send_midi((240, 0, 32, 107, 127, 66, 2, 0 , 16, 112, 0, 247))
    
