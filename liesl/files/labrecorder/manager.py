# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:16:33 2019

@author: Robert Guggenberger
"""
import os
from pathlib import Path
from typing import List, Set, Union
from liesl.streams.finder import open_streaminfo
from liesl.streams._xmltodict import parse as xml_to_dict


def validate(streamargs: List[dict]) -> Set[str]:
    """"checks whether all streams indicated by the streamargs are identifiable
    
    args
    ----
    streamsargs: List[dict]
        a list of keyword-arguments as dictionary. Each entry identifies a specific stream. 


    returns
    -------
    streamids: Set[str]
        a set of validated unique stream ids

    If less streams are found than required, the streamargs identify a single outlets multiple times, or one arg maps to multiple outlets, a connection error will be raised.

    Example::

        sids = validate([{"name":"Liesl-Mock-EEG"},                         
                         {"name":"Liesl-Mock-Marker"}])

    """
    sids = []
    for streamarg in streamargs:
        sinfo = open_streaminfo(**streamarg)
        if sinfo is not None:
            uid = xml_to_dict(sinfo.as_xml())["info"]["uid"]
            sids.append(uid)

    if len(sids) < len(streamargs):
        raise ConnectionError("Not all streams were found")
    elif len(set(sids)) < len(streamargs):
        # the set contains unique source-ids multiple times
        raise ConnectionError("Some streams were selected multiple times")
    else:
        return sids


def add_to_path(path):
    os.system('setx path "%path%;{0:s}"'.format(path))


def follow_lnk(path):
    "follow a lnk file on windows"
    import win32com.client

    path = str(path)
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    return Path(shortcut.Targetpath)


def find_file(path="~", file="LabRecorderCLI.exe") -> Union[Path, None]:
    """find a file recursively
    
    args
    ----
    path:str
        the root folder
    file:str
        the file name
    
    returns
    -------
    filepath: Union[Path, None]
        the path to the file or nothing
    """
    path = Path(str(path)).expanduser().absolute()
    for i in path.glob("**/*"):
        if i.name == file:
            return i

