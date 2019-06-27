from subprocess import PIPE, Popen
from pathlib import Path
from liesl.files.labrecorder.manager import follow_lnk, find_file, validate
from liesl.files.run import Run
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

    if path_to_cmd.suffixes[-1]   == ".lnk":
        path_to_cmd = follow_lnk(path_to_cmd).parent / "LabRecorderCLI.exe"
        if not path_to_cmd.exists():
            raise FileNotFoundError("Path to command does not exist")
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
    def bind(self, streamargs:List[dict,]=[None]) -> None:
        """bind a set of required streams to start recording
        Recording will throw a ConnectionError if these streams are not present 
        at time of binding or at the time of starting a recording        
        """
        self.streamargs = validate(streamargs) if streamargs is not None \
                                                                    else None
    def validate(self):
        validate(self.streamargs)
    
    def __init__(self, path_to_cmd:str="~") -> None:
        self.streamargs= None
        self.cmd = find_lrcmd(path_to_cmd)
                
    def __enter__(self):        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if exc_type is ConnectionError:
                print(exc_value)
                raise exc_type("Not all required streams were found")
            else:
                raise exc_type
    
    def start_recording(self, filename:str="~/recordings/recording.xdf",
                        streamargs:List[dict,]=None) -> None:
        
        if streamargs is not None:
            self.streamargs = self.bind(streamargs)
            
        if self.streamargs is None:
            raise ValueError("No streams were specified")
            
        filename = Run(filename)   
        filename.parent.mkdir(exist_ok=True, parents=True)
        
        # start encoding the command 
        streams = ""
        for si, sargs in enumerate(self.streamargs):
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
        
        # start the recording process
        self.process = Popen(' '.join( (str(self.cmd),
                                        str(filename),
                                        str(streams)) ),
                             stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)           
        peek =  self.process.stdout.peek()
        if b'matched no stream' in peek:            
            self.stop_recording()
            print('\a') #makes a platfrom independent beep
            raise ConnectionError(peek.decode().strip())            
        self.t0 = time.time()
        logger.info('Start recording to {0}'.format(filename))


    def close(self) -> None:
        self.stop_recording()
        
    def stop_recording(self) -> None:        
        if hasattr(self, 'process'):       
            o, e = self.process.communicate(b'\n')
            if self.process.poll() != 0:
                raise ConnectionError(o + e)            
            del self.process
            self.dur = time.time()-self.t0
        logger.info('Stopped recording after {0}s'.format(self.dur))
        
# %%