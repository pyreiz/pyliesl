from liesl.files.labrecorder.cli_wrapper import LabRecorderCLI as Recorder
from typing import List
from pathlib import Path
from contextlib import contextmanager
# %%  
class Session():
    '''Class resembling a whole session

    Example::

        # create a new folder for storing the session data
        session = Session(r'C:\\projects\\recording','')
        # populate the configuration
        session.header.gender = 'F'
        session.header.name = 'Paula_Unknown'
        # dump all recordings to session-specific folder
        session.dump()

    '''
    def __init__(self, 
                 prefix:str="VvNn",
                 mainfolder:str=r"~/labrecordings", 
                 recorder:Recorder=None,
                 streamargs:List[dict]=[None],
                 ):
        self.prefix = Path(prefix)
        self.mainfolder = Path(mainfolder).expanduser().absolute()
        self.folder = (self.mainfolder / self.prefix)
        self.folder.mkdir(exist_ok=True, parents=True)
        if Recorder is None:
            raise ValueError("No recorder specified")
        else:
            self.recorder = recorder
        self.recorder.bind(streamargs)
        
    def start_recording(self, task:str="recording"):        
        fname = self.folder / Path(task + ".xdf")
        fname.parent.mkdir(exist_ok=True, parents=True)  
        self.recorder.start_recording(fname)
        
    def stop_recording(self):
        self.recorder.stop_recording()
    
    @contextmanager
    def __call__(self, task:str="recording"):
        self.start_recording(task)
        yield self
        self.stop_recording()
    