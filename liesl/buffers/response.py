# -*- coding: utf-8 -*-
"""
Responses
---------
"""
from typing import Tuple, List
import numpy as np
from numpy import ndarray


class Response:
    """A reponse to a trigger

    args
    ----
    chunk:np.ndarray
        a data chunk as received from pylsl.StreamInlet.pull_chunk() or :meth:`liesl.buffers.ringbuffer.RingBuffer.get`
        should be  2-dimensional (samples x channels)
    tstamps:np.ndarray          
        the timestamps of this  data chunk as e.g. received from pylsl.StreamInlet.pull_chunk() or :meth:`liesl.buffers.ringbuffer.RingBuffer.get`
        can be 1-dimensional (timepoints) or 2 dimensional (timepoints x 1)
    onset_in_ms:float
        the timestamp of the trigger as e.g. received from 
        pylsl.StreamInlet.pull_sample() 
    fs:int
        sampling rate in Hz, defaults to 1000
    pre_in_ms:float
        how many milliseconds to use before the trigger
    post_in_ms:float
        how many milliseconds to use after the trigger
    ep_window_in_ms:Tuple[float, float]
        the expected timeframe when the evoked potential starts and stops. defaults to [15,50]

    """

    def __init__(
        self,
        chunk: np.ndarray,
        tstamps: np.ndarray,
        onset_in_ms: float,
        fs: int = 1000,
        pre_in_ms: float = 30,
        post_in_ms: float = 75,
        ep_window_in_ms: Tuple[float, float] = (15.0, 50.0),
    ):
        if tstamps.ndim == 1:
            tstamps = np.atleast_2d(tstamps).T

        if chunk.ndim == 1:
            raise ValueError("Chunk must be 2D of form (samples x channels)")

        self.chunk = chunk
        self.tstamps = tstamps
        self.onset_in_ms = onset_in_ms
        self.fs = fs
        self.pre_in_ms = pre_in_ms
        self.post_in_ms = post_in_ms
        self.ep_window_in_ms = ep_window_in_ms

    @property
    def onset(self) -> int:
        onset = abs((self.onset_in_ms - self.tstamps)[:, 0]).argmin()
        return onset

    @property
    def pre(self) -> int:
        pre = int(self.pre_in_ms * 1000 / self.fs)
        return self.onset - pre

    @property
    def post(self) -> int:
        post = int(self.post_in_ms * 1000 / self.fs)
        return self.onset + post

    @property
    def ep_window(self) -> List[int]:
        ep_window = [self.onset + int(m * 1000 / self.fs) for m in self.ep_window_in_ms]
        return ep_window

    def get_trace(
        self, channel_idx: int = 0, baseline_correction: bool = True
    ) -> ndarray:
        """Cuts a chunk of data

        Based on the given onset this function cuts out a trace
        for one or more (if an slice is given) channel. It does a baseline
        correction by default.

        args
        ----
        channel_idx:int
            which channel to use for calculation of latency.
           

        returns
        -------
        trace: np.ndarray
            Contains the trace of the data cut from pre to post around the onset. Type is a ndarray containing (pre+post) samples and shape (samples, 1)
            
        """
        response = self.chunk[self.pre : self.post, channel_idx].copy()
        if baseline_correction:
            bl = self.chunk[self.pre : self.onset + 1, channel_idx]
            response -= bl.mean()
        return response

    def get_latency(self, channel_idx: int = 0) -> List[float]:
        """the latency of the MEP in a specific channel

        Based on the time of TMS given during initialization, and the hard-coded
        pre_in_ms, post_in_ms and ep_window_in_ms calculates the latency 

        args
        ----
        channel_idx:int
            which channel to use for calculation of latency

        returns
        -------
        vpp: List[float]
            the latency in ms relative to the TMS pulse of the negative and the
            positive peak
        """

        bl = self.chunk[self.pre : self.onset, channel_idx].mean(0)
        data = self.chunk[self.ep_window[0] : self.ep_window[1] + 1, channel_idx] - bl
        peakpos = [data.argmin(), data.argmax()]
        peakpos = [p + self.ep_window[0] for p in peakpos]
        peakpos_in_ms = [float(p - self.onset) * 1000 / self.fs for p in peakpos]
        return peakpos_in_ms

    def get_vpp(self, channel_idx: int = 0) -> ndarray:
        """the peak-to-peak amplitude of the MEP in a specific channel

        Based on the time of TMS given during initialization, and the hard-coded
        pre_in_ms, post_in_ms and ep_window_in_ms calculates the Vpp

        args
        ----
        channel_idx:int
            which channel to use for calculation of Vpp

        returns
        -------
        vpp:np.ndarray
            the peak-to-peak amplitude in native units of the data chunk
        """
        bl = self.chunk[self.pre : self.onset, channel_idx].mean(0)
        data = self.chunk[self.ep_window[0] : self.ep_window[1] + 1, channel_idx] - bl
        peakpos = [data.argmin(), data.argmax()]
        self.peakpos = [p + self.ep_window[0] for p in peakpos]
        self.peakpos_in_ms = [
            p * 1000 / self.fs + self.ep_window_in_ms[0] + self.pre_in_ms
            for p in peakpos
        ]
        self.peakval = [data.min(), data.max()]
        return data.max() - data.min()

    def get_xaxis(
        self, stepsize: float = 5
    ) -> Tuple[ndarray, List[str], Tuple[int, int]]:
        """get xaxis objects for plotting

        args
        ----
        stepsize: float
            the size of the stepos between xticks


        returns
        --------
        xticks:ndarray
            an array of xticks
        xticklabels:List[str]
            a list fo xticklabels
        xlim: Tuple[int, int]
            the limits of the xaxis
        """
        if stepsize <= 0:
            raise ValueError("Stepsize must be larger than 0")
        xticks = np.arange(0, self.post - self.pre, stepsize * 1000 / self.fs)
        xlim = (0, self.post - self.pre)
        xticklabels = [
            "{0:.0f}".format(x)
            for x in np.arange(
                -self.pre_in_ms * 1000 / self.fs,
                (self.post_in_ms + stepsize) * 1000 / self.fs,
                stepsize,
            )
        ]
        return xticks, xticklabels, xlim

    def as_json(self, channel_idx: int = 0) -> str:
        """encodes the response as json

        args
        ----
        channel_idx:int
            which channel to use for calculation of MEP parameters

        returns
        -------
        msg:str
            a json-encoded dictionary to be e.g. sent wwith an LSL MarkerOutlet
        
        """
        bl = self.chunk[self.pre : self.onset + 1, channel_idx].mean(0)
        data = self.chunk[self.ep_window[0] : self.ep_window[1] + 1, channel_idx] - bl
        mi, ma = [data.min(), data.max()]
        max_latency = self.get_latency(channel_idx)[0]

        msg = (
            '{"mepmaxtime": '
            + f"{max_latency:.2f}, "
            + '"mepamplitude": '
            + f"{ma-mi:.2f}, "
            + '"mepmin": '
            + f"{mi:.2f}, "
            + '"mepmax": '
            + f"{ma:.2f}"
            + "}"
        )
        return msg


class MockResponse(Response):
    """mocks a response for testing and development"""

    def __new__(cls):
        tstamps = np.linspace(0, 1, 1001)
        chunk = np.arange(0, 1000, dtype=float)
        chunk = np.repeat(np.atleast_2d(chunk).T, 8, 1)
        onset_in_ms = tstamps[500]
        return Response(
            chunk=chunk,
            tstamps=tstamps,
            onset_in_ms=onset_in_ms,
            fs=1000,
            pre_in_ms=50,
            post_in_ms=50,
            ep_window_in_ms=[15, 50],
        )
