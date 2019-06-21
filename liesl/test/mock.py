#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:15:38 2019

@author: Robert Guggenberger

"""

import time
from random import random as rand
from random import choice
from pylsl import StreamInfo, StreamOutlet, local_clock
import threading
# %%
class Mock(threading.Thread):
    
    def __init__(self, name='MockEEG',
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
        self.channel_count = channel_count
        self.samplestep = 1/nominal_srate
    
    def stop(self):
        self.is_running = False
        self.join()
        
    def run(self):
                
        self.is_running = True
        print("now sending data...")
        outlet = StreamOutlet(self.info)
        while self.is_running:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            mysample = [rand() for c in range(self.channel_count)]
            # now send it and wait for a bit
            outlet.push_sample(mysample)
            time.sleep(self.samplestep)
            
    def __str__(self):
        return self.info.as_xml()
    
    
class MarkerMock(Mock):
    
    def __init__(self, name='MockMarker',
                 type='Marker',
                 channel_count=1,
                 nominal_srate=0,
                 channel_format='string',
                 source_id=None,
                 markernames = ['Test', 'Blah', 'Marker', 'XXX', 'Testtest', 'Test-1-2-3']):
        
        threading.Thread.__init__(self)

        if source_id == None:
            source_id = str(hash(self))
            
        self.info = StreamInfo(name, type, channel_count, nominal_srate,  
                               channel_format, source_id)        
        self.channel_count = channel_count
        self.markernames = markernames
        
    def generate_marker(self):        
        while True:
            yield [choice(self.markernames)]
        
    def run(self):                
        self.is_running = True
        print("now sending data...")
        outlet = StreamOutlet(self.info)
        markers = self.generate_marker()
        while self.is_running:
            sample = next(markers)
            tstamp = local_clock()
            print(f"Pushed {sample} at {tstamp}")
            outlet.push_sample(sample, tstamp)
            time.sleep(rand())
            


    
