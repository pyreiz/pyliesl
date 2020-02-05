"""
Session
-------

"""
from liesl.files.labrecorder.cli_wrapper import LabRecorderCLI as Recorder
from typing import List
from pathlib import Path
from contextlib import contextmanager


class Session:
    """Manages recordings for a whole session

    Example::

        streamargs = [{'name':"localite_marker", "hostname": localhostname},
                      {'name':"reiz_marker_sa", "hostname": localhostname},
                      {'name':"BrainVision RDA Markers", "hostname": localhostname},
                      {'name':"BrainVision RDA", "hostname": localhostname}]
        
        session = Session(prefix="VvNn",
                          streamargs=streamargs)


        with session("task"):
            run_task() 
            #  run your task, and while it runs, the streams are recorded
            # to ~/labrecording/VvNn/task_R001.xdf


        with session("task"):
            run_task() 
            # run your task, and while it runs, the streams are recorded 
            # to ~/labrecording/VvNn/task_R002.xdf
        
        with session("othertask"):
            run_othertask() 
            # run your task, and while it runs, the streams are recorded 
            # to ~/labrecording/VvNn/othertask_R001.xdf
    """

    def __init__(
        self,
        prefix: str = "VvNn",
        mainfolder: str = "~/labrecordings",
        recorder: Recorder = None,
        streamargs: List[dict] = [None],
    ):
        self.prefix = Path(prefix)
        self.mainfolder = Path(mainfolder).expanduser().absolute()
        self.folder = self.mainfolder / self.prefix
        self.folder.mkdir(exist_ok=True, parents=True)
        if recorder is None:
            self.recorder = Recorder()
        else:
            self.recorder = recorder
        self.recorder.bind(streamargs)
        self._is_recording = False

    def start_recording(self, task: str = "recording"):
        """start recording all streams 
        
        args
        ----
        task:str
            the name of the file. will be instantiated as a :class:`~liesl.files.run.Run` and therefore auto-increment

        """
        if self._is_recording:
            raise FileExistsError("Am currently recording. Stop first")
        fname = self.folder / Path(task + ".xdf")
        fname.parent.mkdir(exist_ok=True, parents=True)
        print("Saving to", self.recorder.start_recording(fname))
        self._is_recording = True

    def stop_recording(self):
        "stop the current recording"
        self.recorder.stop_recording()
        self._is_recording = False

    @contextmanager
    def __call__(self, task: str = "recording"):
        self.start_recording(task)
        yield self
        self.stop_recording()

