from subprocess import PIPE, Popen
from pathlib import Path
from liesl.files.labrecorder.manager import follow_lnk, find_file, validate
from liesl.files.run import Run
import logging
import time
from typing import List
import pkg_resources
import sys


def find_lrcmd_os(platform: str) -> Path:
    "return the default path to labrecorder for this platform"
    root = Path(pkg_resources.resource_filename("liesl", "files/labrecorder/lib"))
    if "linux" in platform:
        path_to_cmd = root / "LabRecorderCLI"
    elif "win" in platform:
        path_to_cmd = root / "LabRecorderCLI.exe"
    else:
        raise NotImplementedError()
    if path_to_cmd.exists() == False:
        path_to_cmd = "~"
    return path_to_cmd


def find_lrcmd(path_to_cmd: str = None) -> Path:
    "Find and validate the path to LabRecorder"
    if path_to_cmd is None:
        path_to_cmd = find_lrcmd_os(sys.platform)
    path_to_cmd = Path(str(path_to_cmd)).expanduser().absolute()

    if not path_to_cmd.exists():
        raise FileNotFoundError("Path to command does not exist")

    if "linux" in sys.platform:
        if path_to_cmd.name == "LabRecorderCLI":
            return path_to_cmd
    elif "win" in sys.platform:
        if path_to_cmd.name == "LabRecorderCLI.exe":
            return path_to_cmd

    # if nothing worked, we end here
    raise FileNotFoundError("No valid path to LabRecorder")


class LabRecorderCLI:
    """Process based interface for LabRecorder
        
    Example::
                      
        filename = '~/Desktop/untitled.xdf'
        streamargs = [{"type":"EEG"},{"type":"Marker"}]
        streamargs = [{"type":"EEG", "name":"Liesl-Mock-EEG"},              
                      {"type":"Marker"}]
        lr = LabRecorderCLI()   
        lr.start_recording(filename, streamargs)       
        time.sleep(5)    
        lr.stop_recording()
        
    """

    def bind(self, streamargs: List[dict,] = [None]) -> None:
        """bind a set of required streams to start recording
        Recording will throw a ConnectionError if these streams are not present 
        at time of binding or at the time of starting a recording        
        """
        self.streamargs = validate(streamargs) if streamargs is not None else None

    def validate(self):
        validate(self.streamargs)

    def __init__(self, path_to_cmd: str = "~") -> None:
        self.streamargs = None
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

    def start_recording(
        self,
        filename: str = "~/recordings/recording.xdf",
        streamargs: List[dict,] = None,
    ) -> None:

        if streamargs is not None:
            self.bind(streamargs)

        if self.streamargs is None:
            raise ValueError("No streams were specified")

        filename = Run(filename)
        filename.parent.mkdir(exist_ok=True, parents=True)

        # start encoding the command
        streams = ""
        for si, sargs in enumerate(self.streamargs):
            stream = '"'
            for i, (k, v) in enumerate(sargs.items()):
                prt = f"{k}='{v}'"
                if i > 0:
                    prt = " and " + prt
                stream += prt
            stream += '"'
            if si > 0:
                stream = " " + stream
            streams += stream

        # start the recording process
        self.process = Popen(
            " ".join((str(self.cmd), str(filename), str(streams))),
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            bufsize=1,
        )
        peek = self.process.stdout.peek()
        if b"matched no stream" in peek:
            self.stop_recording()
            print("\a")  # makes a platfrom independent beep
            raise ConnectionError(peek.decode().strip())
        self.t0 = time.time()
        print("Start recording to {0}".format(filename))

    def close(self) -> None:
        self.stop_recording()

    def stop_recording(self) -> None:
        if hasattr(self, "process"):
            o, e = self.process.communicate(b"\n")
            if self.process.poll() != 0:
                raise ConnectionError(o + e)
            del self.process
            self.dur = time.time() - self.t0
        print("Stopped recording after {0}s".format(self.dur))

