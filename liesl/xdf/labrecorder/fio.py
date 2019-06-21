# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:16:33 2019

@author: Robert Guggenberger
"""
import os
from pathlib import Path
# %%
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
        
class Run(): 
    #inherits from path by overriding __new__
    def __new__(cls, fname:str):
        fname = Path(str(fname)).expanduser().absolute()
        if fname.suffix == "":
            fname = fname.with_suffix(".xdf")
        if fname.suffix != ".xdf":
            raise ValueError("Please specify a correct .xdf file")
        
        count = 0
        base_stem = fname.stem.split('_R')[0]
        for f in fname.parent.glob(fname.stem + "*.xdf"):            
            base_stem, run_counter = f.stem.split('_R')
            count = max(int(run_counter), count)
        count += 1
        run_str = "_R{0:03d}".format(count)
        
        final_name = fname.with_name(base_stem + run_str).with_suffix('.xdf')
        return Path(final_name)
    