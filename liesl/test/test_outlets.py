# -*- coding: utf-8 -*-
"""Example program to demonstrate how to send a multi-channel time-series
with proper meta-data to LSL."""

import threading
import random
import time
from pylsl import StreamInfo, StreamOutlet, local_clock
    
def start_outlet(mode='cont'):
    if mode == 'cont':
        t = test_outlet_continuous()
        t.start()
    
class test_outlet_continuous(threading.Thread):

    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def stop(self):
        self.keep_running = False
    
    def run(self):
        # first create a new stream info 
        info = StreamInfo('Liesl', 'EEG', 8, 100, 'float32', 'mock_stream_liesl')
        
        # append some meta-data
        info.desc().append_child_value("manufacturer", "BioSemi")
        channels = info.desc().append_child("channels")
        for c in ["C3", "C4", "Cz", "FPz", "POz", "CPz", "O1", "O2"]:
            channels.append_child("channel")\
                .append_child_value("name", c)\
                .append_child_value("unit", "microvolts")\
                .append_child_value("type", "EEG")
        
        # next make an outlet; we set the transmission chunk size to 32 samples and
        # the outgoing buffer size to 360 seconds (max.)
        outlet = StreamOutlet(info, 32, 360)
        
        print("now sending data...")
        self.keep_running = True
        while self.keep_running:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            mysample = [random.random(), random.random(), random.random(),
                        random.random(), random.random(), random.random(),
                        random.random(), random.random()]
            # get a time stamp in seconds (we pretend that our samples are actually
            # 1ms old, e.g., as if coming from some external hardware)
            stamp = local_clock()-0.001
            # now send it and wait for a bit
            outlet.push_sample(mysample, stamp)
            time.sleep(0.01) # wait a ms to maintain the fs