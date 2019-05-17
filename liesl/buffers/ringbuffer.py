# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 09:43:32 2018

@author: AGNPT-M-001
"""
import numpy as np
import logging
logger = logging.getLogger(__name__.split('.')[-1])
# %%
class SimpleRingBuffer():
    
    def __init__(self, rowlen:int, columnlen:int, verbose=False) -> None:
        self.max_row = int(rowlen)
        self.max_column = int(columnlen)
        self.verbose = verbose
        self.reset()
            
    def reset(self):
        self.buffer = np.empty( (0, self.max_column) ) 
        
    
    def put(self, chunk:list or np.ndarray, transpose=False):           
        """append a chunk of data and delete old samples
        
        should be faster than the implementation using np.roll according to 
        https://gist.github.com/cchwala/dea03fb55d9a50660bd52e00f5691db5
        
        """        
        chunk = np.atleast_2d(chunk)
        if self.verbose:
            if chunk.shape[0] > self.max_row:            
                logger.warning('Ringbuffer Overflow')            
            
        if transpose:
            chunk = chunk.T
            
        buffer = np.concatenate( (self.buffer, chunk), axis=0)        
        if buffer.shape[0] > self.max_row:                               
            self.buffer = buffer[-self.max_row:, :]
        else:
            self.buffer = buffer

    def get_only(self, rowslices=None, colslices=None) -> np.ndarray:
        'return none or a slice of the ringbuffer'        
        try:
            (r,c) = self.buffer.shape
            if not rowslices:            
                rowslices = slice(0, r, 1)
            if not colslices:
                colslices = slice(0, c, 1)
            return self.buffer[rowslices,colslices].copy()
        except AttributeError:
            return None
        
    def get(self) -> np.ndarray:       
        'return none or the ringbuffer'        
        try:
            return self.buffer.copy()
        except AttributeError:
            return None
        
    @property
    def is_full(self):
        return self.buffer.shape[0] == self.max_row
    
    @property
    def shape(self):
        return self.buffer.shape
    
    @property
    def maxshape(self):
        return (self.max_row, self.max_column)


class LabStreamRingBuffer():
    
    def __init__(self, duration_in_ms:float=1000):
        self.duration_in_ms = duration_in_ms    
        
    def reset(self):
        'initializes or resets the buffer' 
        logger.info(f'{self} was reset') 
        fs = int(self.info['nominal_srate'])
        if fs <= 0:
            logger.warning(f'Unspecified sampling rate: {fs}, assume 1000 Hz')
            fs = 1000
        max_samples = int( self.duration_in_ms * (fs/1000))        
        channel_count = int(self.info['channel_count'])
        self._buffer = SimpleRingBuffer(max_samples=max_samples, 
                                        channel_count=channel_count)
        self._novel = False
       
    def _handle(self, chunk:np._NoValue) -> None:
        self._novel = True
        self._buffer.put(chunk)
    
    def put(self, item):
        'handles the items put into the inbox and transforms them into the buffer'
        if item is None:
            pass
        elif type(item) is dict:            
            self.info = item
            self.reset()
        elif type(item) is tuple:
            chunk, timestamps = item
            self._buffer.handle_chunk(np.hstack( 
                    (np.atleast_2d(chunk), np.atleast_2d(timestamps))))            
        elif type(item) is np.ndarray:
            self._handle(item)       
        else:
            logger.warning(
                    'Unknown item of type {0}. Skipping'.format(type(item)))        
    
    def _get_current(self) -> np.ndarray:
        self._novel = False
        return self._buffer.get()
    
    def get(self) -> np.ndarray:
        if self._novel:
            return self._get_current()
        else:
            return None
        
    @property
    def shape(self):
        return self._buffer.shape
    
    @property
    def maxshape(self):
        return self._buffer.maxshape
# %%
def _test_raw_ring():

    import matplotlib.pyplot as plt
    ring= SimpleRingBuffer(1000, 64)
    while True:
        chunk = np.random.random((50, 64))
        ring.append(chunk)
        print(ring.buffer.shape)
        plt.cla()
        plt.plot(ring.buffer[:, 0])
        plt.pause(0.001)
        
def _timeit_raw_ring():
    #%%timeit
    ring= SimpleRingBuffer(1000, 64)
    chunk = np.random.random((50, 64))
    for i in range(1):    
        ring.put(chunk)
    
# %%
if __name__ == '__main__':
    from .receiver import LabStreamReceiver    
    from .blockbuffer import LabStreamBlockBuffer
    from pylsl import local_clock as time    
    import matplotlib.pyplot as plt
    stream = LabStreamReceiver(type='EEG')
    stream.start()   
    
    bbuffer = LabStreamBlockBuffer(block_in_ms=100)
    rbuffer = LabStreamRingBuffer(duration_in_ms=1000)
    stream.subscribe(bbuffer) 
    while not hasattr(bbuffer, 'info'):
        pass
    else:
        rbuffer.put(bbuffer.info)
    t0 = time()
    T0 = t0
    cnt = 0.
    while True:
        chunk = bbuffer.get()
        rbuffer.put(chunk)
        ring = rbuffer.get()
        if ring is not None:
            cnt+=1.
            t1 = time()
            print(ring.shape, t1-t0, (t1-T0)/cnt)
            t0=t1
            plt.cla()
            plt.plot(ring[:,0])
            plt.pause(0.001)