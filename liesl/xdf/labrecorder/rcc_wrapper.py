# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:14:39 2019

@author: Messung
"""


import socket
class LabRecorderRCC():
    '''Remote Control Client for the LabRecoder Remote Control Server
    
    Example::
        
        import time
        lr = LabRecorderRCC(host='127.0.0.1', port=7000)
        lr.start_recording()
        print('start recording')
        time.sleep(10)
        print('stop recording')
        time.sleep(2)
        lr.stop_recording()
        
    .. warning::
    
        Turn on RCS in the GUI first.
        
    '''
    _msg_start = 'start\n'.encode('ascii')
    _msg_stop = 'stop\n'.encode('ascii')
    
    def __init__(self, host:str='127.0.0.1', port:int=7000,
                 timeout:float=None) -> None:
        self.host = host
        self.port = port      
        self.timeout = timeout
        
    def connect(self):        
        self.connected = False
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface.settimeout(self.timeout)
        while not self.connected:
            try: 
                # state = 'onnected'
                self.interface.connect((self.host, self.port))
                self.connected = True                
                
            except socket.timeout as e:
                # state = 'time_out'
                raise socket.timeout('Check whether LabRecorder is ' +
                                             'running and RCS is turned on')
    
    def await_ok(self):
        msglen = 0
        msgbuf = b''
        while msglen < 2:            
            msg = self.interface.recv(2 - msglen)
            msgbuf += msg
            msglen = len(msgbuf)            
        if msgbuf != b'OK':
            raise ConnectionError('Command not confirmed')
    
    def start_recording(self):
        self.connect()
        self.interface.send(self._msg_start)
        self.await_ok()
        self.close()
        
    def stop_recording(self):
        self.connect()
        self.interface.send(self._msg_stop)
        self.await_ok()
        self.close()
        
    def close(self):
        self.interface.close()
        del self.interface