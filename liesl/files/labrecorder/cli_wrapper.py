"""
LabRecorderCLI
--------------
"""

from subprocess import PIPE, Popen, run
from pathlib import Path
from liesl.files.labrecorder.manager import find_file, validate
from liesl.files.run import Run
import logging
import time
from typing import List
import pkg_resources
import sys


def find_lrcmd_os(platform: str) -> Path:
    "return the default path to labrecorder for this platform"
    root = Path(
        pkg_resources.resource_filename("liesl", "files/labrecorder/lib")
    )
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
    """Process based interface for LabRecorderCLI

    args
    ----
    path_to_cmd:str
        defaults to None and select the LabRecorder installed in liesl/files/labrecorder/lib. Otherwise, use the path to the LabRecorderCLI of your desire.


    Use :meth:`~.start_recording` and :meth:`~.stop_recording` to record a set of streams identified by keyword arguments.

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

    def __init__(self, path_to_cmd: str = None) -> None:
        self.streamargs = None
        self.cmd = find_lrcmd(path_to_cmd)

    def bind(self, streamargs: List[dict,] = [None]) -> None:
        """bind a set of required streams to start recording
        Recording will throw a ConnectionError if these streams are not present
        at time of binding or at the time of starting a recording
        """
        self.streamargs = (
            validate(streamargs) if streamargs is not None else None
        )

    def start_recording(
        self,
        filename: str = "~/recordings/recording.xdf",
        streamargs: List[dict,] = None,
    ):
        "start recording the streams identified by streamargs to filename"

        if streamargs is not None:
            self.bind(streamargs)

        if self.streamargs is None:
            raise ValueError("No streams were specified")

        filename = Run(filename)
        filename.parent.mkdir(exist_ok=True, parents=True)

        # start encoding the command
        streams = []
        for idx, uid in enumerate(self.streamargs):
            stream = '"'
            prt = f"source_id='{uid}'"
            stream += prt
            stream += '"'
            streams.append(stream)

        cmd = " ".join((str(self.cmd), str(filename), *streams))

        if "win" in sys.platform:
            self.process = Popen(
                cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1,
            )
        else:  # linux
            self.process = Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                bufsize=1,
                shell=True,
            )
        peek = self.process.stdout.peek()
        # print(peek.decode())
        if b"matched no stream" in peek:  # pragma no cover
            # would be already catched by self.validate
            self.stop_recording()
            print("\a")  # makes a platfrom independent beep
            raise ConnectionError(peek.decode().strip())
        self.t0 = time.time()
        print("Start recording to {0}".format(filename))
        return filename

    def stop_recording(self) -> None:
        "stop recording"
        if hasattr(self, "process"):
            o, e = self.process.communicate(b"\n")
            if self.process.poll() != 0:  # pragma no cover
                raise ConnectionError(o + e)
            del self.process
            self.dur = time.time() - self.t0
        print("Stopped recording after {0}s".format(self.dur))

