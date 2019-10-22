# -*- coding: utf-8 -*-
"""TMS Response class

@author:  Robert Guggenberger
"""
from dataclasses import dataclass
import numpy as np
# %%
@dataclass
class Response():    
    """A MEP reponse to a TMS pulse

    required during initialization are

    args
    ----
    chunk:np.ndarray
        a data chunk as received from pylsl.StreamInlet.pull_chunk()
    tstamps:np.ndarray
        the timestamps of this  data chunk as received from pylsl.StreamInlet.pull_chunk()
    onset_in_ms:float
        the timestamp of the TMS pulse as e.g. received from 
        pylsl.StreamInlet.pull_sample() (i.e. slightly delayed)
        or coil.trigger(), i.e. when command was sent

    """
    chunk:np.ndarray
    tstamps:np.ndarray
    onset_in_ms:float
    fs:int = 1000
    pre_in_ms:float = 30
    post_in_ms:float = 75
    mep_window_in_ms = [15, 50]
    
    
    @property
    def onset(self):       
        onset = abs((self.onset_in_ms-self.tstamps)[:,0]).argmin()
        return onset 

    @property
    def pre(self):
        pre = int(self.pre_in_ms*1000/self.fs)
        return self.onset-pre

    @property
    def post(self):
        post = int(self.post_in_ms*1000/self.fs)
        return self.onset+post
    
    @property
    def mep_window(self):
        mep_window = [self.onset+int(m*1000/self.fs) 
                        for m in self.mep_window_in_ms]
        return mep_window
    
    def get_trace(self, channel_idx = 0, baseline_correction:bool = True):
        """Cuts a chunk of data

        Based on the given onset this function cuts out a trace
        for one or more (if an slice is given) channel. It does a baseline
        correction by default.

        args
        ----
        channel_idx
            which channel to use for calculation of latency.
            Can be int or slice (to get multiple channels)

        returns
        -------
        trace: np.ndarray
            numpy arrray of shape (pre+post, channels)
            Contains the trace or traces if multiple channels where given
        """
        response = self.chunk[self.pre:self.post, channel_idx].copy()     
        if baseline_correction:
            bl = self.chunk[self.pre:self.onset, channel_idx] 
            response -= bl.mean()
        return response

    def get_latency(self, channel_idx:int=0):
        """the latency of the MEP in a specific channel

        Based on the time of TMS given during initialization, and the hard-coded
        pre_in_ms, post_in_ms and mep_window_in_ms calculates the latency 

        args
        ----
        channel_idx:int
            which channel to use for calculation of latency

        returns
        -------
        vpp: List[np.ndarray,np.ndarray]
            the latency in ms relative to the TMS pulse of the negative and the
            positive peak
        """

        bl = self.chunk[self.pre:self.onset, channel_idx].mean(0)        
        data = self.chunk[self.mep_window[0]:self.mep_window[1], channel_idx]-bl        
        peakpos = [data.argmin(), data.argmax()]
        peakpos = [p + self.mep_window[0] for p in peakpos]
        peakpos_in_ms = [p*1000/self.fs -
                         self.onset_in_ms
                         for p in peakpos]   
        return peakpos_in_ms
    
    def get_vpp(self, channel_idx:int=0):      
        """the peak-to-peak amplitude of the MEP in a specific channel

        Based on the time of TMS given during initialization, and the hard-coded
        pre_in_ms, post_in_ms and mep_window_in_ms calculates the Vpp

        args
        ----
        channel_idx:int
            which channel to use for calculation of Vpp

        returns
        -------
        vpp:np.ndarray
            the peak-to-peak amplitude in native units of the data chunk
        """
        bl = self.chunk[self.pre:self.onset, channel_idx].mean(0)        
        data = self.chunk[self.mep_window[0]:self.mep_window[1], channel_idx]-bl        
        peakpos = [data.argmin(), data.argmax()]
        self.peakpos = [p + self.mep_window[0] for p in peakpos]
        self.peakpos_in_ms = [p*1000/self.fs + self.mep_window_in_ms[0] + 
                                self.pre_in_ms for p in peakpos]        
        self.peakval = [data.min(), data.max()]
        return data.max()-data.min()
    
    def remove_jitter(self, break_threshold_seconds=1,
                      break_threshold_samples=500):
        "deprecated: would remove jitter, but did reduce timing accuracy"              
        nsamples = len(self.tstamps)
        tdiff = 1.0 / self.fs if self.fs > 0 else 0.0
        self.rawtstamps = self.tstamps.copy()        
        if nsamples > 0 and self.fs > 0:
            # Identify breaks in the data
            diffs = np.diff(self.tstamps,axis=0)
            breaks_at = diffs > np.max((break_threshold_seconds,
                                        break_threshold_samples * tdiff))
            if np.any(breaks_at):
                indices = np.where(breaks_at)[0]
                indices = np.hstack((0, indices, indices, nsamples - 1))
                ranges = np.reshape(indices, (2, -1)).T
            else:
                ranges = [(0, nsamples - 1)]
    
            # Process each segment separately
            samp_counts = []
            durations = []
            self.effective_srate = 0
            for range_i in ranges:
                if range_i[1] > range_i[0]:
                    # Calculate time stamps assuming constant intervals
                    # within the segment.
                    indices = np.arange(range_i[0], range_i[1] + 1, 1)[:, None]
                    X = np.concatenate((np.ones_like(indices), indices), axis=1)
                    y = self.tstamps[indices,0]
                    mapping = np.linalg.lstsq(X, y, rcond=-1)[0]
                    self.tstamps[indices,0] = (mapping[0] + mapping[1] *
                                                   indices)
                    # Store num_samples and segment duration
                    samp_counts.append(indices.size)
                    durations.append((self.tstamps[range_i[1]] -
                                      self.tstamps[range_i[0]]) + tdiff)
            samp_counts = np.asarray(samp_counts)
            durations = np.asarray(durations)
            if np.any(samp_counts):
                self.effective_srate = np.sum(samp_counts) / np.sum(durations)
        else:
            self.effective_srate = 0
     
    def get_xaxis(self, stepsize=5):
        "returns xticks, xticklabels and xlim for plotting with matplotlib"
        
        xticks = np.arange(0, self.post-self.pre, stepsize*1000/self.fs)
        xlim = (0, self.post-self.pre)
        xticklabels = (['{0:.0f}'.format(x) for x in np.arange(
                        -self.pre_in_ms*1000/self.fs, 
                        (self.post_in_ms+stepsize)*1000/self.fs, stepsize)])
        return xticks, xticklabels, xlim
    
    def as_json(self, channel_idx:int=0):
        """encodes the response as json

        args
        ----
        channel_idx:int
            which channel to use for calculation of MEP parameters

        returns
        -------
        msg:str
            a json-encoded dictionary to be sent to localite with 
            _`coil.send_response`
        """
        bl = self.chunk[self.pre:self.onset, channel_idx].mean(0)        
        data = self.chunk[self.mep_window[0]:self.mep_window[1], channel_idx]-bl    
        mi,ma = [data.min(), data.max()]        
        max_latency = self.get_latency(channel_idx)[0]
        
        msg = ('{"mepmaxtime": ' + f"{max_latency:.2f}, " + 
               '"mepamplitude": ' + f"{ma-mi:.2f}, " + 
               '"mepmin": ' + f"{mi:.2f}, " + 
               '"mepmax": ' + f"{ma:.2f}" + '}')
        return msg
        
class MockResponse():
    "mocks a response for testing and development"
    def __new__(cls):
        return Response(chunk=np.random.random((1000,8)),
                   tstamps=np.atleast_2d(np.linspace(0,1000,1000)).T,
                   fs=1000,
                   onset_in_ms=501)
                   
