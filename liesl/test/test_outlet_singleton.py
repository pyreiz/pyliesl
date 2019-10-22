#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 19:09:52 2019

@author: rgugg
"""

import unittest
from liesl.outlet.singleton import SingletonOutlet
from liesl import available_streams
  
class Test(unittest.TestCase):

    def setUp(self):    
        print("Setting up")
        self.outlet = SingletonOutlet()
     
    def test_info_identity(self):
        streams = available_streams()
        print(streams[0].as_xml())
        for attr in ['channel_count', 'channel_format',
                     'hostname', 'name', 'nominal_srate', 'session_id', 
                     'source_id', 'type', 'uid', 'version']:
            with self.subTest(msg=f'{attr} failed'):
                send = getattr(self.outlet.info, attr)()   
                recv = getattr(streams[0], attr)()
                print(attr, send, recv)
                self.assertEqual(send, recv)

    def tearDown(self):
        print("Tearing down")
        del self.outlet

if __name__ == '__main__':
    unittest.main()
