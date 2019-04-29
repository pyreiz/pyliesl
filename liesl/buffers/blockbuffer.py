# -*- coding: utf-8 -*-
import numpy as np
from collections import deque
import logging
logger = logging.getLogger(__name__)
# %%
class RawBlockBuffer():
    
    def __init__(self, rowlen, columnlen):
        self.buffer = np.empty( (rowlen, columnlen) ) 
        self.buffer.fill(None)
        self.head = iter(range(0, rowlen, 1))
    
    def append(self, sample):
        'append a column of data but raise a StopIteration when full'        
        head = next(self.head)
        self.buffer[head,:] = sample        
    
class SimpleBlockBuffer():
    '''Appends incoming data and publishes them in blocks.   
    
    All created blocks are stored in a queue and are available 
    via :method:`~.get`
    '''
    def __init__(self, max_samples=50, channel_count=64, max_queued=None):
        self.max_samples = max_samples        
        self.channel_count = channel_count
        self.max_queued = max_queued 
        self.reset()                
        
    def reset(self):
        'clear all buffers and the queue'        
        self.queue = deque(maxlen=self.max_queued)        
        self.buffer = RawBlockBuffer(rowlen=self.max_samples, 
                                     columnlen=self.channel_count)
        self.last_block = None
        self.stop_asap = False
        self.has_stopped = False

    def handle_sample(self, sample):
        'try to append new samples to the block'
        if not self.has_stopped:
            try:
                self.buffer.append(sample)
            except StopIteration: #when the RawBlockBuffer is full
                self.queue.append(self.buffer.buffer)
                if not self.stop_asap:
                    self.buffer = RawBlockBuffer(self.max_samples, self.channel_count)            
                    self.buffer.append(sample)
                else:
                    self.has_stopped = True
                    
    def handle_chunk(self, chunk):
        '''iteratively append all samples of a chunk to the block
        args
        ----
        chunk:np.ndarray
            a new chunk of data to be processed columnwise
        '''       
        for sample in chunk:          
            self.handle_sample(sample)            
    
    def terminate(self):
        self.stop_asap = True
    
    def get_last(self):
        'return the last valid block'
        return self.last_block
    
    def get(self):
        'return none or a block if there is one waiting in the queue'
        try:
            block = self.queue.pop()
            self.last_block = block
            return block
        except IndexError:
            return None
# %%
def test_SimpleBlockBuffer():
    blockbuffer = SimpleBlockBuffer(50, 64)
    # %%
    expected = [False, False, True, False]
    received = []
    for i in range(0,4,1):
        chunk = np.random.random( (25, 64))
        blockbuffer.handle_chunk(chunk)
        block = blockbuffer.get()
        if block is not None:
            print('Gotcha')
            received.append(True)
        else:
            print('Nada')
            received.append(False)
    assert all([e == r for e,r in zip(expected, received)])
