# -*- coding: utf-8 -*-
"""
Minmaxbuffer memorizes the minimum and maximum

"""
class MinMaxBuffer():
    
    def __init__(self, buffer, minimum=0, maximum=2, current_slice=None, chan=0):
        self.buffer = buffer
        self.minimum = 0
        self.maximum = maximum
        if current_slice is None:
            current_slice = buffer.maxshape[0]
        self.current_slice = current_slice
        self.chan = chan
        
    def get_level(self):
        chunk, tstamp = self.buffer.get()
        try:        
            data = chunk[:,self.chan] #.tolist()
            level = chunk[-self.current_slice:,:].mean()
            #data.append(self.minimum)
            #data.append(self.maximum)
            self.maximum = max(data)
            self.minimum = min(data)
            return (level - self.minimum)/self.maximum
        except Exception as e:
            print(e)
            return 0

    def get_percent(self):
        percent = self.get_level()*100
        percent = max((min((percent, 100)),0))
        return percent
       
    @property
    def shape(self):
        return self.memlen