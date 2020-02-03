# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 09:43:32 2018

@author: AGNPT-M-001
"""
import numpy as np
import logging
from typing import Union


class SimpleRingBuffer:
    def __init__(self, rowlen: int, columnlen: int, verbose=False) -> None:
        """a simple ringbuffer

        args
        ----
        rowlen: int
            the number of samples
        columnlen:int
            the number of channels
        verbose:bool {False}
            how verbose the buffer should be
            
        Example
        -------
            rb = SimpleRingBuffer(1000, 2)

        """
        self.max_row = int(rowlen)
        self.max_column = int(columnlen)
        self.verbose = verbose
        self.reset()

    def reset(self):
        "empty the internal buffer"
        self.buffer = np.empty((0, self.max_column))

    def put(self, chunk: Union[list, np.ndarray], transpose=False):
        """append a chunk of data and delete old samples
        
        should be faster than the implementation using np.roll according to 
        https://gist.github.com/cchwala/dea03fb55d9a50660bd52e00f5691db5
        
        """
        chunk = np.atleast_2d(chunk)
        if self.verbose:
            if chunk.shape[0] > self.max_row:
                print("Ringbuffer Overflow")

        if transpose:
            chunk = chunk.T

        buffer = np.atleast_2d(np.concatenate((self.buffer, chunk), axis=0))
        if buffer.shape[0] > self.max_row:
            self.buffer = buffer[-self.max_row :, :]
        else:
            self.buffer = buffer

    def get(self) -> np.ndarray:
        "return a copy of the internal buffer"
        return self.buffer.copy()

    @property
    def is_full(self) -> bool:
        "whether the internal buffer is full or not"
        return self.buffer.shape[0] == self.max_row

    @property
    def shape(self):
        "the current size of the internal buffer"
        return self.buffer.shape

    @property
    def max_shape(self):
        "the maximal size of the internal buffer"
        return (self.max_row, self.max_column)
