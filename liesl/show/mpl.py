# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 17:14:40 2019

@author: Trainer
"""

import matplotlib.pyplot as plt
import liesl
# %%
stream = liesl.open_stream(type='Acc', hostname='TRAINER-001')
buffer = liesl.RingBuffer(stream, duration_in_ms=1000)
buffer.start()
fig, ax = plt.subplots(1,1)
while plt.fignum_exists(fig.number):
    plt.pause(0.05)
    ax.cla()    
    ax.plot(buffer.get())
    ax.legend(('x','y','z'), loc='upper left')