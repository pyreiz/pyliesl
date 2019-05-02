# -*- coding: utf-8 -*-
"""
Threaded ring and blockbuffers
"""
import threading
import weakref
import time
from liesl.buffers.ringbuffer import SimpleRingBuffer
#%%
class RingBuffer(threading.Thread):
    
    def __init__(self, stream, duration_in_ms:float=1000, verbose=False) -> None:
        threading.Thread.__init__(self)
        self.stream = weakref.ref(stream)
        self.fs = stream.info().nominal_srate()
        max_row = int(duration_in_ms * (self.fs/1000))
        max_column = int(stream.info().channel_count())
        self.buffer = SimpleRingBuffer(rowlen=max_row, columnlen=max_column,
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
    
    def stop(self):
        self.is_running = False
        
    def run(self):
        self.is_running = True
        while self.is_running:
            chunk, tstamp = self.stream().pull_chunk()        
            if chunk:
                self.bufferlock.acquire()
                self.buffer.put(chunk)
                self.bufferlock.release()
            else:
                time.sleep(10/self.fs)
    