"""
BlockBuffer
-----------
"""
import numpy as np
from collections import deque
from typing import Union
from numpy import ndarray

# %%
class RawBlockBuffer:
    def __init__(self, rowlen: int, columnlen: int) -> None:
        self.buffer = np.empty((rowlen, columnlen))
        self.buffer.fill(None)
        self.head = iter(range(0, rowlen, 1))

    def append(self, sample: ndarray):
        "append a column of data but raise a StopIteration when full"
        head = next(self.head)
        self.buffer[head, :] = sample


class SimpleBlockBuffer:
    """Convert incoming data into blocks.   
    
    Put new samples or chunks using :meth:`~.handle_sample` or :meth:`~.handle_chunk`. The SimpleBlockBuffer takes the data, and only publishes full blocks. These blocks are available by calling  :meth:`~.get`

    args
    ----
    max_samples:int
        how many samples (rowlen) each block should have
    channel_count:int
        how many channels (columnlen) each block should have
    max_queued: Union[None, int]
        Whether to queue as many blocks as possible (None) or drop if more than max_queued


    Example::

        blockbuffer = SimpleBlockBuffer(50, 1)
        chunk = np.arange(0, 200)
        blockbuffer.handle_chunk(chunk)
        block = blockbuffer.get()      
        assert block[0] == 0.0 # the first block starts with the first sample
        block = blockbuffer.get()      
        assert block[0] == 50.0 # the second block starts with the 50th sample
        assert block.shape == [50, 1]  # as defined during initalization

    """

    def __init__(self, max_samples=50, channel_count=64, max_queued=None):
        self.max_samples = max_samples
        self.channel_count = channel_count
        self.max_queued = max_queued
        self.reset()

    def reset(self):
        "clear all buffers and the queue"
        self.queue = deque(maxlen=self.max_queued)
        self.buffer = RawBlockBuffer(
            rowlen=self.max_samples, columnlen=self.channel_count
        )
        self.last_block = None

    def handle_sample(self, sample):
        "try to append new samples to the block"
        try:
            self.buffer.append(sample)
        except StopIteration:  # when the RawBlockBuffer is full
            self.queue.append(self.buffer.buffer)
            self.buffer = RawBlockBuffer(self.max_samples, self.channel_count)
            self.buffer.append(sample)

    def handle_chunk(self, chunk):
        """iteratively append all samples of a chunk to the block
        args
        ----
        chunk:np.ndarray
            a new chunk of data to be processed columnwise
        """
        for sample in chunk:
            self.handle_sample(sample)

    def get_last(self):
        "return the last valid block"
        return self.last_block

    def get(self) -> Union[None, ndarray]:
        "return none or a block if there is one waiting in the queue"
        try:
            block = self.queue.popleft()
            self.last_block = block
            return block.copy()
        except IndexError:
            return None
