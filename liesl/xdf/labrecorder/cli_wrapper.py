from subprocess import PIPE, Popen
from pathlib import Path
from liesl.xdf.labrecorder.fio import Run, follow_lnk, find_file
import logging
import time
from typing import List
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
# %%                  

def find_lrcmd(path_to_cmd:str="~"):
    path_to_cmd = Path(str(path_to_cmd)).expanduser().absolute()
    if not path_to_cmd.exists():
        raise FileNotFoundError("Path to command does not exist")
    
    # this is the full correct path to command
    if path_to_cmd.name == "LabRecorderCLI.exe":
        return path_to_cmd
    
    # the command is directly in the folder 
    pospath = (path_to_cmd / "LabRecorderCLI.exe")
    pospath = pospath if pospath.exists() else None
    if pospath is not None:
        return pospath
    
    # there is a link on the desktop, useful because the default folder is "~"
    pospath = follow_lnk(find_file(Path(path_to_cmd) / "Desktop",
                                   file="LabRecorder.lnk"))
    if pospath is not None and pospath.name == "LabRecorderCLI.exe":
        return pospath
    
    # there is the file somewhere in a subfolder 
    pospath= find_file(path_to_cmd, file="LabRecorderCLI.exe")
    if pospath is not None:
        return pospath 
    
    # there is a link somewhere in a subfolder 
    pospath = follow_lnk(find_file(Path(path_to_cmd),
                                   file="LabRecorder.lnk"))
    if pospath is not None and pospath.name == "LabRecorderCLI.exe":
        return pospath
    
    #if nothing worked, we end here
    raise FileNotFoundError("Path to command not found")
        
class LabRecorderCLI():
    '''Process based interface for LabRecorder
        
    Example::
                      
        filename = '~/Desktop/untitled.xdf'
        streamargs = [{"type":"EEG"},{"type":"Marker"}]
        streamargs = [{"type":"EEG", "name":"Liesl-Mock"},{"type":"Marker"}]
        lr = LabRecorderCLI()   
        lr.start_recording(filename, streamargs)       
        time.sleep(5)    
        lr.stop_recording()
        
    '''
    def __init__(self, path_to_cmd:str="~") -> None:    
        self.cmd = find_lrcmd(path_to_cmd)
                
    def start_recording(self, filename:str="~/recordings/recording.xdf",
                        streamargs:List[dict,]=None) -> None:
        if streamargs is None:
            raise ValueError("No streams were specified")
        
        filename = Run(filename)   
        filename.parent.mkdir(exist_ok=True, parents=True)
        
        streams = ""
        for si, sargs in enumerate(streamargs):
            stream = "\""
            for i, (k,v) in enumerate(sargs.items()):                            
                prt = f"{k}='{v}'"    
                if i > 0:
                    prt = " and " + prt
                stream += prt            
            stream += "\""
            if si>0:
                stream = " " + stream
            streams += stream 
        
        self.process = Popen(' '.join( (str(self.cmd),
                                        str(filename),
                                        str(streams)) ),
                             stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)           
        peek =  self.process.stdout.peek()
        if b'matched no stream' in peek:            
            raise ConnectionError(peek.decode().strip())
        self.t0 = time.time()
        logger.info('Start recording to {0}'.format(filename))

    def stop_recording(self) -> None:        
        if hasattr(self, 'process'):       
            o, e = self.process.communicate(b'\n')
            if self.process.poll() != 0:
                raise ConnectionError(o + e)            
        dur = time.time()-self.t0
        logger.info('Stopped recording after {0}s'.format(dur))
        
# %%