#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:18:45 2019

@author: rgugg
"""
import threading
from pylsl import StreamOutlet, StreamInfo
import socket
import json
# %%

class KillableOutlet(threading.Thread):
    
    def __init__(self, info:StreamInfo, receive_data:callable, host:str="127.0.0.1", port:int=9991):
        threading.Thread.__init__(self)
        self.info = info
        self.receive_data = receive_data
        self.host = host
        self.port = port
        self.is_running = threading.Event()
        

      
    def swallow_poison(self, client):
        'receive byte for byte the message'
        #parse the message until it is a valid json 
        msg = bytearray(b' ')
        while True:
            try:
                prt = client.recv(1)                    
                msg += prt                  
                pill = json.loads(msg.decode('ascii')) # because the first byte is b' '         
            except json.decoder.JSONDecodeError:
                pass
            except Exception as e:
                print(e)
                break
        if pill == {'poison':'pill'}:
            self.is_running.clear()            
        client.shutdown(2)
        client.close()
        self.close()
        
    def close(self):
        self.join()

    def run(self):
        outlet = StreamOutlet(self.info)                
        poisonpill = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        poisonpill.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        poisonpill.bind((self.host, self.port))
        poisonpill.interface.listen(1)
        self.is_running.set() #sets true
        while self.is_running:
            chunk = self.receive_data
            outlet.push_chunk(chunk)
            client, address = poisonpill.accept()
            self.swallow_poison(client)
        del poisonpill, outlet
# %%
class KillerClient():    
    
    def __init__(self, host:str="127.0.0.1", port:int=9991):
        self.host = host
        self.port = port       
        
    def push(self, marker:str='', tstamp:float=None):
        'connects, sends a message, and close the connection'        
        self.connect()
        self.write(marker, tstamp)
        self.close()            
    
    def connect(self):
        'connect wth the remote server'
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface.connect((self.host, self.port))
        self.interface.settimeout(3)
  
    def write(self, marker, tstamp):
        'encode message into ascii and send all bytes'        
        msg = json.dumps((marker, tstamp)).encode('ascii')
        print(f'Sending {marker} at {tstamp}')
        self.interface.sendall(msg)

    def close(self):
        'closes the connection'
        self.interface.shutdown(1)
        self.interface.close()