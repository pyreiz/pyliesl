# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:16:33 2019

@author: Robert Guggenberger
"""
import os
from pathlib import Path
# %%
def validate(streamargs):
    from liesl.streams.finder import get_source_id
    sids = []
    # use only dictionaries which are unique
    _streamargs = set([tuple(s.items()) for s in streamargs])
    
    for _s in _streamargs:
        s = dict(_s)
        print("Looking for", s, end="")
        try: 
            sids.append(get_source_id(**s))
            print(" found")
        except TimeoutError:
            print(" not found")
            
    if len(sids) < len(_streamargs):        
        raise ConnectionError("Not all streams were found")
    elif len({s["source_id"] for s in sids}) < len(_streamargs):
        # the set contains unique source-ids
        raise ConnectionError("Some streams were selected multiple times")    
    else:
        return sids
        
def add_to_path(path):
    os.system('setx path "%path%;{0:s}"'.format(path))

def follow_lnk(path):
    path = str(path)
    import win32com.client 
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    return Path(shortcut.Targetpath)

def find_file(path="~", file="LabRecorderCLI.exe"):        
    path = Path(str(path)).expanduser().absolute()
    for i in path.glob('**/*'):
        if (i.name == file):                   
            return i     

    