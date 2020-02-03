"""
Ringbuffer
----------
"""
from liesl.streams.convert import inlet_to_dict
from pylsl import StreamInlet, StreamInfo
import numpy as np
from numpy import ndarray
from typing import Union, Tuple
import threading
import time


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


# -------------------------------------------------------------------------------


class RingBuffer(threading.Thread):
    """A ringbuffer subscribed to an LSL outlet
    
    The ringbuffer automatically updating itself as a thread.

    args
    ----
    streaminfo: StreamInfo
        identifies the StreamOutlet and will be connected once the buffer started
    duration_in_ms: float
        the length of the ringbuffer in ms. is automatically converted into samples based on the nominal sampling rate of the LSL Outlet. All data older than duration_in_ms (normalized by expected samples) will be discarded
    verbose:bool
        how verbose the ringbuffer should be. defaults to False
    

    Example::
    
       sinfo = get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
       # the mock EEG has a sampling rate of 100 and 8 channels
       rb = RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
       rb.await_running()
       time.sleep(1) # wait a second to collect sufficient data 
       chunk, tstamps = rb.get()
       assert chunk.shape == [100, 8] # for 1s of data and 8 channels
    

    """

    def __init__(
        self,
        streaminfo: StreamInfo,
        duration_in_ms: float = 1000,
        verbose: bool = False,
    ) -> None:

        threading.Thread.__init__(self)
        self.streaminfo = streaminfo
        fs = streaminfo.nominal_srate()
        if fs == 0:  # pragma no cover
            self.fs = 1000
            print(
                "Irregular sampling rate. Assuming fs=1000 and "
                + "convert duration_in_ms into duration_in_samples"
            )
        else:
            self.fs = fs
        max_row = int(duration_in_ms * (self.fs / 1000))
        max_column = int(streaminfo.channel_count())
        self.buffer = SimpleRingBuffer(
            rowlen=max_row, columnlen=max_column, verbose=verbose
        )
        self.tstamps = SimpleRingBuffer(rowlen=max_row, columnlen=1, verbose=verbose)
        self.bufferlock = threading.Lock()
        self._is_running = threading.Event()

    def reset(self):
        "clear the internal buffer and start collecting fresh"
        self.bufferlock.acquire()
        self.buffer.reset()
        self.bufferlock.release()

    def get_data(self) -> ndarray:
        """get only the current data without timestamps

        returns
        -------
        chunk: ndarray
            the data (usually in samples x channels)
        
        
        """
        with self.bufferlock:
            buffer = self.buffer.get()
        return buffer

    def get(self) -> Tuple[ndarray, ndarray]:
        """get the current data with timestamps
        
        returns
        -------
        chunk: ndarray
            the data (usually in samples x channels)
        tstamps: ndarray
            the timestamps for each sample       
        
        """
        with self.bufferlock:
            buffer = self.buffer.get()
            tstamps = self.tstamps.get()
        tstamps += self.offset
        return buffer, tstamps

    @property
    def shape(self) -> Tuple[int, int]:
        "the current size of the data currently in the ringbuffer"
        return self.buffer.shape

    @property
    def max_shape(self) -> Tuple[int, int]:
        "the maximal size of the ringbuffer"
        return self.buffer.max_shape

    @property
    def is_full(self) -> bool:
        "whether the ringbuffer is full"
        return self.buffer.shape[0] == self.buffer.max_shape[0]

    def stop(self):
        "stop the subscription to the outlet"
        self.is_running = False
        self.join()

    @property
    def is_running(self):
        "whether the ringbuffer is receiving new data or not"
        return self._is_running.is_set()

    @is_running.setter
    def is_running(self, state: bool):
        if state:
            self._is_running.set()
        else:
            self._is_running.clear()

    def await_running(self):
        "block until the buffer has subscribed to the LSL outlet"
        print("[", end="")
        try:
            self.start()
        except RuntimeError:  # pragma no cover
            pass
        while not self.is_running:
            time.sleep(0.1)
            print(".", end="")
        print("]")

    def run(self):
        """"""
        stream = StreamInlet(
            self.streaminfo
        )  # create the inlet locally so it can be properly garbage collected
        self.info = inlet_to_dict(stream)
        self.offset = stream.time_correction()
        self.is_running = True
        while self.is_running:
            chunk, tstamp = stream.pull_chunk()
            if chunk:
                with self.bufferlock:  # to prevent writing while reading
                    self.buffer.put(chunk)
                    self.tstamps.put(tstamp, transpose=True)
            else:
                time.sleep(0.001)  # can prevent hiccups when run in a repl
