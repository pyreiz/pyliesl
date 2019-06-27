# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:48:36 2019

@author: Robert Guggenberger
"""

import reiz
import threading
import liesl
# %%
class FeedbackBar(threading.Thread):
    
    def __init__(self, buffer:liesl.RingBuffer, channel:int=0, threshold:float=20,
                 ylim:float=100, samplestep=0.1) -> None:
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.ylim = ylim
        self.channel = channel
        self.is_running = threading.Event()
        self.is_running.clear()
        self.samplestep = samplestep 
        
    @property
    def available(self):
        return self.is_running.is_set()
        
    def run(self):        
        canvas = reiz.Canvas()
        canvas.open()
        self.is_running.set()        
        
        backbar = reiz.visual.Bar(height=1, width=0.2)
        while self.is_running.is_set():
            data = self.buffer.get_data()                     
            if self.channel is not None:
                data = data[:,self.channel]                
            vpp = data.ptp()
            level = vpp/self.ylim
            frontbar = reiz.visual.Bar(height=level, width=0.19, color='red')
            cue = reiz.Cue(visualstim=[backbar, frontbar])
            cue.show(canvas)
            reiz.clock.sleep(self.samplestep)
        
        canvas.close()

def main(**kwargs):   
    channel = kwargs.get("channel", None)
    if "channel" in kwargs:                      
        del kwargs["channel"]        
    
    info = liesl.get_streaminfo_matching(**kwargs)    
    buffer = liesl.RingBuffer(info, duration_in_ms=1000)
    buffer.start()
    buffer.await_running()
    bar = FeedbackBar(buffer=buffer, channel=channel,
                      threshold=kwargs.get("threshold",20),
                      ylim=kwargs.get("ylim",100),
                      samplestep=kwargs.get("samplestep",0.1))
    bar.start()
    