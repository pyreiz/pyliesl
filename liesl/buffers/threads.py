# -*- coding: utf-8 -*-
"""
Threaded ring and blockbuffers
"""
import threading
import time
from liesl.buffers.ringbuffer import SimpleRingBuffer
from liesl.streams.convert import inlet_to_dict
from pylsl import StreamInlet

#%%
class RingBuffer(threading.Thread):
    def __init__(
        self, streaminfo, duration_in_ms: float = 1000, verbose=False, fs=None
    ) -> None:
        threading.Thread.__init__(self)
        self.streaminfo = streaminfo
        if fs is None:
            fs = streaminfo.nominal_srate()
        if fs == 0:
            self.fs = 1000  # convert duration_in_ms into duration_in_samples
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
        self.bufferlock.acquire()
        self.buffer.reset()
        self.bufferlock.release()

    def get_data(self):
        with self.bufferlock:
            buffer = self.buffer.get()
        return buffer

    def get_timed(self):
        return self.get()

    def get(self):
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
        self.is_running.clear()
        self.join()

    @property
    def is_running(self):
        return self._is_running.is_set()

    @is_running.setter
    def is_running(self, state: bool):
        if state:
            self._is_running.set()
        else:
            self._is_running.clear()

    def await_running(self):
        print("[", end="")
        while not self.is_running:
            time.sleep(0.1)
            print(".", end="")
        print("]")

    def run(self):
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

