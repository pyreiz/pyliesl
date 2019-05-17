# -*- coding: utf-8 -*-
"""
Threaded ring and blockbuffers
"""
import threading
import time
from liesl.buffers.ringbuffer import SimpleRingBuffer
#%%
class RingBuffer(threading.Thread):
    
    def __init__(self, stream, duration_in_ms:float=1000, verbose=False, fs=None) -> None:
        threading.Thread.__init__(self)
        self.stream = stream
        if fs is None:
            fs = stream.info().nominal_srate()                
        if fs == 0:
            self.fs = 1000 #convert duration_in_ms into duration_in_samples                
        else:
            self.fs =fs
        max_row = int(duration_in_ms * (self.fs/1000))
        max_column = int(stream.info().channel_count())
        self.buffer = SimpleRingBuffer(rowlen=max_row, columnlen=max_column,
                                       verbose=verbose)
        self.tstamps = SimpleRingBuffer(rowlen=max_row, columnlen=1,
                                       verbose=verbose)
        self.bufferlock = threading.Lock()
        
    def reset(self):
        self.bufferlock.acquire()
        self.buffer.reset()
        self.bufferlock.release()
        
    def get(self):
        self.bufferlock.acquire()
        buffer = self.buffer.get()            
        self.bufferlock.release()
        return buffer

    def get_timed(self):
        with self.bufferlock:
            buffer = self.buffer.get()    
            tstamps = self.tstamps.get()           
        tstamps += self.offset
        return buffer, tstamps
    
    
    @property
    def shape(self):
        return self.buffer.shape
    
    @property
    def maxshape(self):
        return self.buffer.maxshape
    
    def stop(self):
        self.is_running = False
        
    def run(self):
        self.is_running = True
        self.offset = self.stream.time_correction()
        while self.is_running:
            chunk, tstamp = self.stream.pull_chunk()                
            if chunk:
                with self.bufferlock:
                    self.buffer.put(chunk)
                    self.tstamps.put(tstamp, transpose=True)              
            else:
                time.sleep(0.001)
    