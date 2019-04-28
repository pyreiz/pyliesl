# -*- coding: utf-8 -*-
import queue
from abc import ABCMeta, abstractmethod
from typing import Callable, Any
import logging
logger = logging.getLogger(__name__.split('.')[-1])
# %%
class Publisher():
    
    def __init__(self):
        self.subscribers = []

    def stop(self):
        for observer in self.subscribers:
            self.unsubscribe(observer)            
        
    def subscribe(self, observer:Callable[[Any,], None]):
        if observer not in self.subscribers:
            self.subscribers.append(observer)
            logger.info(f'Added {observer} to subscribers')
        else:
            logger.info(f'{observer} already subscribed')
    
    def unsubscribe(self, observer:Callable[[Any,],None]):
        if observer in self.subscribers:            
            observer(StopAsyncIteration)
            self.subscribers.remove(observer)
            logger.info(f'Removed {observer} from subscribers')
        else:
            logger.info(f'{observer} has no subscription')    
 
    def publish(self, item:Any):
        '''publish to all subscribers 
        
        using the callable the subscribers submitted at subscription
        '''
        for observer in self.subscribers:
            observer(item)
                    

# %%

class SimpleObserver(object, metaclass=ABCMeta):
    '''Abstract class for subscriptions to services
    
    ensures that the observers wrap __call__(item) with self.put(item)
    and support self.get()  and self.reset()
    
    The subscriber is informed by the end of the subscription from
    the service side by receiving a `StopAsyncIteration`
    
    '''
    InboxEmpty = queue.Empty
    InboxFull = queue.Full
    Cancelled = StopAsyncIteration
    
    def __init__(self, owner=None): 
        if owner is None:
            self.owner = self.__class__.__name__.split('.')[-1]
        else:
            self.owner=str(owner)
        
    @abstractmethod
    def reset(self):
        'initatializes or resets the buffer' 
        logger.info(f'{self} was reset')    
            
    @abstractmethod
    def put(self, item):
        'puts an item into the subscriptions inbox'        
        
    @abstractmethod
    def get(self):
        'retrieves from the subscriptions buffer'
            
    def __call__(self, item):
        '''allows to call the instance directly instead of its put method
        
        This additional layer of encapsulation can also allow to switch e.g. 
        between push and pull Observers at runtime
        '''
        self.put(item)

    def __repr__(self):
        return self.owner
    
# %%
class Observer(SimpleObserver):
    '''Abstract class for subscriptions to services
    
    ensures an additional abstraction layer around self.put using an inbox 
    scheme, which are handled by self.handle_inbox
    
    The subscriber is informed by the end of the subscription from
    the service side by receiving a `StopAsyncIteration`
    
    '''    
    def __init__(self, maxlen=0, timeout=1, block=False, owner=None): 
        super().__init__(owner)
        self.maxlen = maxlen
        self.block = block
        self.timeout = timeout
        self.received = 0.
        self.missed = 0.
        self.reset()
           

    @abstractmethod
    def handle_inbox(self, item):
        'handles the items put into the inbox and transforms them into the buffer'
                
# -----------------------------------------------------------------------------
class PullAbo(Observer):
    '''keeps items in inbox after receiving it
    
    if the inbox is full, discards the oldest item without handling it    
    '''
    def reset(self):
        super().reset()
        self.inbox = queue.Queue(self.maxlen)         
          
    def put(self, item):        
        try:
            self.inbox.put(item)             
        except self.InboxFull:
            self.missed += 1.
            item = self.buffer.get(timeout=self.timeout)
            self.inbox.task_done()
            self.inbox.put(item)
        self.received += 1.        
        
    def handle_inbox(self):
        try:
            item = self.inbox.get(block=self.block, timeout=self.timeout)
            self.inbox.task_done()
        except self.InboxEmpty:
            item = None
        self.item = self.plugin(item)
        
    @staticmethod
    def plugin(item):
        'overwrite, will manipulate inbox before appending to buffer'
        return item
    
    def join(self):
        self.inbox.join()
        
    def get(self):
        self.handle_inbox()
        return self.item

# -----------------------------------------------------------------------------
class PushAbo(Observer):
    '''any items put into the inbox are immediatly handled
    
    new items are put into a list buffer with maxlen length
    '''       
    def reset(self):
        super().reset()
        self.inbox = None
        self.buffer = []
        
    def put(self, item):
        self.inbox = item
        self.received += 1.
        self.handle_inbox()
        
    def handle_inbox(self):        
        self.inbox = self.plugin(self.inbox)
        self.buffer.append(self.inbox)
        if self.maxlen == 0:
            return
        if len(self.buffer) > self.maxlen:
            self.buffer = self.buffer[-self.maxlen:]
            
    @staticmethod
    def plugin(inbox):
        'overwrite, will manipulate inbox before appending to buffer'
        return inbox
            
    def get(self):
        return self.buffer

# %%

