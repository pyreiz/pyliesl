# -*- coding: utf-8 -*-
import pathlib
import shutil
#%%
libpath = pathlib.Path(__file__).parent
def copy_lsl_api_cfg(targetfile):    
    cfgfile = libpath / "lsl_api.cfg"
    assert cfgfile.exists()    
    targetfile.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(cfgfile, targetfile)
       
def get_target_for_lsl_api_cfg(level:str):
    if level == "system":
        return pathlib.Path(r"C:\etc\lsl_api\lsl_api.cfg")
    elif level =="global":
       return pathlib.Path(r"~/lsl_api/lsl_api.cfg").expanduser()
    elif level =="local":
        return pathlib.Path.cwd()
    
def init_lsl_api_cfg(level:str):
    targetfile = get_target_for_lsl_api_cfg(level)
    copy_lsl_api_cfg(targetfile)
    print("Created a configuration file at", targetfile)