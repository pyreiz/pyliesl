# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 17:14:40 2019

@author: Robert Guggenberger
"""
import matplotlib.pyplot as plt
import liesl
# %%
    
def main(**kwargs):    
    if "channel" in kwargs:          
        limit_channels = True
        channel = kwargs.get("channel")
        del kwargs["channel"]        
    else:
        limit_channels = False
    
    stream = liesl.select_from_available_streams(**kwargs)    
    buffer = liesl.RingBuffer(stream, duration_in_ms=1000)
    buffer.start()
    buffer.await_running()
    labels = []
    try:
        for cix, chan in enumerate(buffer.info['desc']['channels']['channel']):
            if chan['label'] is not None:
                labels.append(chan['label'])
            else:
                labels.append(str(cix)) 
    except:
        for cix in range(int(buffer.info["channel_count"])):
            labels.append(str(cix)) 
    
    
    fig, ax = plt.subplots(1,1)
    while plt.fignum_exists(fig.number):
        plt.pause(0.05)
        ax.cla()
        chunks, tstamp = buffer.get()
        if limit_channels:
            ax.plot(tstamp, chunks[:, channel])
            ax.legend([labels[channel]], loc='upper left')
        else:
            ax.plot(tstamp, chunks)
            ax.legend(labels, loc='upper left')
    
if __name__ == "__main__":
    stream = liesl.open_stream(type='Acc', hostname='TRAINER-001')
    buffer = liesl.RingBuffer(stream, duration_in_ms=1000)
    buffer.start()
    fig, ax = plt.subplots(1,1)
    while plt.fignum_exists(fig.number):
        plt.pause(0.05)
        ax.cla()    
        ax.plot(buffer.get())
        ax.legend(('x','y','z'), loc='upper left')
