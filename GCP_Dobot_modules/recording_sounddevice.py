"""@Author: Sameer Kesava
This module runs on a different thread from
the main program and is for recording audio
to be passed to the DialogFlow methods"""

import threading
import numpy as np
import sounddevice as sd

class record_stream(threading.Thread):
    
    def __init__(self, CHUNK, RATE, CHANNELS, FORMAT):
        threading.Thread.__init__(self)
        #self.lock = threading.Lock()
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        
        

        

    def rec(self):     
            
        return sd.rec(frames=self.CHUNK, samplerate=self.RATE,\
        channels=self.CHANNELS, dtype=self.FORMAT, blocking=True).tobytes()
