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
    sids = [get_source_id(**s) for s in streamargs]
    if len({s["source_id"] for s in sids}) != len(streamargs):
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

    