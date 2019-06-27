#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 12:02:29 2019

@author: rgugg
"""
from time import sleep as pause
    
def cla():
    clear()
    
def clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def linspace(a, b, n=80):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [int(diff * i + a) for i in range(n)]
    
def plot(y, x=None, width=80, height=18):
    """
    Print a crude ASCII art plot
    """
    y_raw = y.copy()    
    
    if x is None:
        x_raw = [x for x in range(len(y))]
    else:
        x_raw = x.copy()    
        
    if len(x_raw) != len(y_raw):
        raise ValueError("Unequal len of x and y")
    
    ma = max(y_raw)    
    mi = min(y_raw)
    a = min(x_raw)
    b =  max(x_raw)
    # Normalize height to screen space
    
    x = linspace(0, len(x_raw)-1, width)        
        
    if ma == mi:
        if ma:
            mi, ma = sorted([0, 2*ma])
        else:
            mi, ma = -1, 1
            
    y = []        
    for ix in x:
        new_y = int(float(height)*(y_raw[ix] - mi)/(ma - mi))
        y.append(new_y) 
        
    margin = max(len(f'{mi}'), len(f'{ma}')) # space left for y-labels
    
    for h in range(height - 1, -1, -1):
        s = [' '] * width
        for x in range(width):
            if y[x] == h:
                if (x == 0 or y[x - 1] == h - 1) and (x == width - 1 or y[x + 1] == h + 1):
                    s[x] = '/'
                elif (x == 0 or y[x - 1] == h + 1) and (x == width - 1 or y[x + 1] == h - 1):
                    s[x] = '\\'
                else:
                    s[x] = '.'

        # Print y values
        if h == height - 1:
            prefix = ("%g" % ma).rjust(margin)[:margin]
        elif h == height//2:
            prefix = ("%g" % ((mi + ma)/2)).rjust(margin)[:margin]
        elif h == 0:
            prefix = ("%g" % mi).rjust(margin)[:margin]
        else:
            prefix = " "*margin
        s = "".join(s)
        if h == height//2:
            s = s.replace(" ", "-")
        print(prefix + " | " + s)

    # Print x values
    bottom = " " * (margin + 3)
    offset = len("%g" % a)
    bottom += ("%g" % a).ljust(width//2 - offset)
    bottom += ("%g" % ((a + b)/2)).ljust(width//2)
    bottom += "%g" % b
    print(bottom)
    

# %%    
def main(**kwargs):
    import liesl
    # %%    
    
    if "channel" in kwargs:        
        channel = kwargs.get("channel")
        del kwargs["channel"]
    else:
        channel = 0
    
    stream = liesl.select_from_available_streams(**kwargs)
    duration = 80*1000/stream.nominal_srate()
    buffer = liesl.RingBuffer(stream, duration_in_ms=duration)
    buffer.start()
    buffer.await_running()
    while buffer.is_running:
        pause(0.05)
        cla()
        chunk, tstamps = buffer.get()
        plot(chunk[:,channel], tstamps)
    # %%
    #%timeit
    
    stream = liesl.open_stream(name="BioSemi", type='EEG')
    stream.time_correction()
    
if __name__ == '__main__':
    
    x = [x for x in range(0,61,1)]
    y = [((x-30)**2)/450 for x in x]    
    
    plot(y, x, width=60)    
    plot(y, x, width=80, height=50)
    plot(y, x, width=40, height=10)
    plot(y,  width=40, height=10)
    
    x = [x for x in range(1,81,1)]
    y = [((x-30)**2)/450 for x in x]    
    plot(y, x, width=80)    
 #%%
 
    from itertools import count, islice, tee    
    from math import sin, pi
    def take(n, it):
       return [x for x in islice(it, n)]

    def drop(n, it):
        return islice(it, n, None) 
    
    
    stream = count()
    while True:
        stream, xstream = tee(stream)
        take(4, stream)
        x = [x for x in islice(xstream, 81)]
        y = [sin(x/80*2*pi) for x in x]
        plot(y, x, width=80, height=20)        
        pause(4/80)
        clear()
        
