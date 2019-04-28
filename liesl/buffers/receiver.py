# -*- coding: utf-8 -*-
from pylsl import StreamInlet
from liesl.abstracts.pubobs import Publisher
from liesl.tools.streams import select_from_available_streams
from liesl.tools.convert import inlet_to_dict
import threading    
import numpy as np
import logging
logger = logging.getLogger(__name__)
# %%
def get_channel_idx(val:str, channels:dict) -> int:
        clab = [entry['label'] for entry in channels]
        idx = [entry['idx'] for entry in channels]
        return idx[clab.index(val)]

class LabStreamReceiver(threading.Thread):
    '''Receives and publishes a LSL stream
        
    args
    ----
    **kwargs: (parm='Value')
        a set of keyword:value pairs to find an appropriate stream, e.g.         
        LabStreamReceiver(type='EEG')
    
    **kwargs: (stream=stream)
        an instance of a pylsl.StreamInlet
        LabStreamReceiver(stream=stream)
        
    **kwargs: None
        Allows you to browse through all available streams and select one 
        interactively
        
    
    The LabStreamReceiver publishes to all observers. Start the receiver and
    subscribe/unsubscribe with :method:`~.LabStreamReceiver.subscribe` and 
    :method:`~.LabStreamReceiver.unsubscribe`
    
    .. seealso::
        API for subscribers/publishers :module:`experiment.realtime.pubobs`
    
    Example:
        receiver = LabStreamReceiver()
        receiver.start()
        
    '''
    
    def __init__(self, append_time=True, **kwargs):  
        threading.Thread.__init__(self)
        if 'stream' in kwargs.keys():
            stream = kwargs['stream']     
            if stream is None:
                raise ValueError('No valid stream defined')
        else:            
            stream = select_from_available_streams(**kwargs)
                
        self.inlet = StreamInlet(stream)        
        self.info = inlet_to_dict(self.inlet) 
   #     self.channels = self.info['desc']['channels']['channel']
        if append_time ==  True:            
#            idx = int(self.info['channel_count'])            
#            self.channels.append({'label':'timestamp',
#                                  'unit':'seconds',
#                                  'type':'Time',
#                                  'idx': idx})
#            self.info['channel_count'] = str(idx + 1)                    
            self.handle_lsl = self._handle_fusion
        else:            
            self.handle_lsl = self._handle_tuple        
        
        self.label_index = lambda x: get_channel_idx(x, self.channels)
   
        self.publisher = Publisher()
        self.check_clock_offset()   

    
        
    def check_clock_offset(self):
        self.clock_offset = max((0, self.inlet.time_correction()))
        logger.info('Checking offset. Set to {0}'.format(self.clock_offset))
    
    def subscribe(self, client):
        '''subscribe the client
        
        informs the subscribed observer about itself by publishing a dict with
        key information (e.g. sampling rate and channel names)
        '''
        client(self.info) #submit a dictionary
        self.publisher.subscribe(client)
    
    def unsubscribe(self, abo):
        self.publisher.unsubscribe(abo)                

    def terminate(self):        
        self.is_running = False        
        logger.debug(f'Shutting down {self}')
        
    def _handle_fusion(self):
        chunk, timestamps = self.inlet.pull_sample()
        if timestamps:
            timestamps += self.clock_offset
            item = np.hstack((np.atleast_2d(chunk), np.atleast_2d(timestamps)))
            return item        
        
    def _handle_tuple(self):
        chunk, timestamps = self.inlet.pull_sample()
        if timestamps:
            timestamps += self.clock_offset            
            return (chunk, timestamps)
        
    def run(self):
        '''publishes the data concatenated with time stamps and transformed to
        a np.ndarray'''
        self.is_running = True
        while self.is_running:
            item = self.handle_lsl()
            if item is not None:
                self.publisher.publish(item)            
                

# %%
if __name__ == '__main__':
    stream = LabStreamReceiver(type='EEG')
    stream.start()
