#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:15:38 2019

@author: Robert Guggenberger

"""

import time
from random import random as rand
from pylsl import StreamInfo, StreamOutlet
import threading
# %%
class Mock(threading.Thread):
    
    def __init__(self, name='BioSemi',
                 type='EEG',
                 channel_count=8,
                 nominal_srate=100,
                 channel_format='float32',
                 source_id=None):
        
        threading.Thread.__init__(self)

        if source_id == None:
            source_id = str(hash(self))
            
        self.info = StreamInfo(name, type, channel_count, nominal_srate,  
                           channel_format, source_id)
        self.outlet = StreamOutlet(self.info)
        self.channel_count = channel_count
    
    def stop(self):
        self.is_running = False
        self.join()
        
    def run(self):
                
        self.is_running = True
        print("now sending data...")
        while self.is_running:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            mysample = [rand() for c in range(self.channel_count)]
            # now send it and wait for a bit
            self.outlet.push_sample(mysample)
            time.sleep(0.01)
            
    def __str__(self):
        return self.info.as_xml()
    
