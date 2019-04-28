# -*- coding: utf-8 -*-
import numpy as np
from collections import deque
from liesl.abstracts.pubobs import SimpleObserver
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
class LabStreamBlockBuffer(SimpleObserver):
    '''Buffers and publishes blocks after subscription to a receiver
    
    args
    ----
    block_in_ms: float
        how long a block lasts in ms 
    
    overflow:int
        how many blocks are queued before the oldest is discarded
    

    '''
    
    def __init__(self, block_in_ms=50, overflow=1000):
        super().__init__()
        self.block_in_ms = block_in_ms             
        self.overflow = overflow
        
    def reset(self):
        'initializes or resets the buffer according to sampling rate' 
        logger.info(f'{self} was reset')
        fs = float(self.info['nominal_srate'])
        if fs <= 0.0:
            logger.warning(f'Unspecified sampling rate: {fs}, assume 1000 Hz')
            fs = 1000
        max_samples = int( self.block_in_ms * (fs/1000))        
        self.info['blocksize'] = max_samples
        channel_count = int(self.info['channel_count'])  
        
        self._buffer = SimpleBlockBuffer(max_samples=max_samples, 
                                         channel_count=channel_count,
                                         max_queued=self.overflow)
    
    def put(self, item):
        'handles the items put into the inbox and transforms them into the buffer'        
        if item is None:
            pass
        elif type(item) is dict:                        
            self.info = item            
            self.reset()
        elif type(item) is tuple:
            chunk, timestamps = item
            self._buffer.handle_chunk(chunk)
        elif type(item) is np.ndarray:
            self._buffer.handle_chunk(item)
        elif item is StopAsyncIteration:
            self._buffer.terminate()
        else:
            logger.warning(
                    'Unknown item of type {0}. Skipping'.format(type(item)))
        
    def get(self):
        'returns the oldest block from the queue'
        return self._buffer.get()

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

# %%
if __name__ == '__main__':
    from liesl.receiver import LabStreamReceiver
    from liesl.test.test_outlets import start_outlet 
    start_outlet('cont')
    from pylsl import local_clock as time
    from time import sleep
    #stream = LabStreamReceiver(name='Liesl', type='EEG')
    stream = LabStreamReceiver(name='faros_acc')
    stream.start()   

    bbuffer = LabStreamBlockBuffer(block_in_ms = 100)
    stream.subscribe(bbuffer) 
    cnt = 0.
    t0 = time()
    T0 = t0
    mn = np.Inf
    mx = -np.Inf
    while True:
        block = bbuffer.get()
        if block is not None:
            t1 = time()            
            cnt += 1.
            fs = 1/np.diff(block[:,-1]).mean()
            print(f'Count# {int(cnt)} received at {(t1-T0)/cnt}, range: {mn} to {mx}, empirical srate:{fs}')
            mn = min(mn, t1-t0)
            mx = max(mx, t1-t0)
            t0 = t1
            sleep(0.01)
    stream.unsubscribe(bbuffer) 