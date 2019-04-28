# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 14:47:30 2019

@author: Trainer
"""
import numpy as np
import matplotlib.pyplot as plt
from liesl.streams.finder import open_stream
from faros_streamer import streamer as faros
# %%
#import os
#os.system('faros --mac EC:FE:7E:16:09:5C --stream')
#available = faros.get_devices()
faros_stop, show_settings = faros.start_streaming_of('EC:FE:7E:16:09:5C')
show_settings()
# %%
stream = open_stream(name='faros_acc', hostname='TRAINER-001')
from liesl import RingBuffer
buffer = RingBuffer(stream=stream, duration_in_ms=1000)
buffer.start()

fig, ax = plt.subplots(1,1)     
while True:
    data = buffer.get()   
    data = data/np.linalg.norm(data.mean(axis=0))
    ax.cla()
    ax.plot(data)
    plt.legend(['x','y','z'])
    (x,y,z)= data[-10:,:].mean(0)
    rad = np.arctan2(x,z)
    angle = np.rad2deg(rad)+180
    if angle > 180:
        angle -= 360
    ax.set_title(angle)
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel('Force along respective axis')
    plt.pause(0.05)
    
buffer.stop()
faros_stop()