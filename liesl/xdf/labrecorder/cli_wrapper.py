from subprocess import PIPE, Popen
from pathlib import Path
from liesl.xdf.labrecorder.fio import Run, follow_lnk, find_file
import logging
logger = logging.getLogger()
import time
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
        streams = "type='EEG' type='Markers'"        
        streams = "type='dfg'"
        streams = "type='EEG'"
        lr = LabRecorderCLI()
        lr.start_recording(streams, filename)        
        time.sleep(5)    
        lr.stop_recording()
        
    '''
    def __init__(self, path_to_cmd:str="~") -> None:    
        self.cmd = find_lrcmd(path_to_cmd)
                
    def start_recording(self, streams:str,
                        filename:str="~/recordings/recording.xdf") -> None:
        filename = Run(filename)   
        filename.parent.mkdir(exist_ok=True, parents=True)
        self.t0 = time.time()
        self.process = Popen(' '.join( (str(self.cmd),
                                        str(filename),
                                        str(streams)) ),
                             stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)   
        peek =  self.process.stdout.peek()
        if b'matched no stream' in peek:            
            raise ConnectionError(peek.decode().strip())
        logger.info('Start recording to {0}'.format(filename))

    def stop_recording(self) -> None:        
        if hasattr(self, 'process'):       
            o, e = self.process.communicate(b'\n')
            if self.process.poll() != 0:
                raise ConnectionError(o + e)            
        dur = time.time()-self.t0
        logger.info('Stopped recording after {0}s'.format(dur))
        
# %%