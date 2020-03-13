"""
XDFStreams
----------
"""
import pyxdf
from typing import List, Union, Any, Dict
from functools import lru_cache
from pathlib import Path
from collections import defaultdict
from numpy import ndarray


def convert_desc(source: defaultdict, target: dict = None):
    if source is None:
        return None
    target = target or dict()
    for key, item in source.items():
        if type(item) == list:
            if len(item) == 1:
                item = item[0]
            else:
                item = [convert_desc(i, dict()) for i in item]
        if type(item) == defaultdict:
            item = convert_desc(item, dict())

        target[key] = item

    return target


class XDFStream:
    """Interface to an XDFstream loaded from an :code:`xdf`-file
    """

    def __init__(self, unparsed_stream: dict):
        self._stream = unparsed_stream
        try:
            self.desc = convert_desc(unparsed_stream["info"]["desc"][0])
        except KeyError:
            self.desc = None

    @property
    @lru_cache(maxsize=1)
    def channel_labels(self) -> Union[List[str], None]:
        "get the channel labels as a list of strings"
        if self.desc is not None:
            return [i["label"] for i in self.desc["channels"]["channel"]]
        else:
            return None

    @property
    @lru_cache(maxsize=1)
    def channel_types(self) -> Union[List[str], None]:
        "get the channel types as a list of strings"
        if self.desc is not None:
            return [i["type"] for i in self.desc["channels"]["channel"]]
        else:
            return None

    @property
    @lru_cache(maxsize=1)
    def channel_units(self) -> Union[List[str], None]:
        "get the channel units as a list of strings"
        if self.desc is not None:
            return [i["unit"] for i in self.desc["channels"]["channel"]]
        else:
            return None

    @property
    @lru_cache(maxsize=1)
    def nominal_srate(self) -> float:
        "get the nominal sampling rate as float"
        return float(self._stream["info"]["nominal_srate"][0])

    @property
    @lru_cache(maxsize=1)
    def channel_count(self) -> int:
        "get the channel count as int"
        return int(self._stream["info"]["channel_count"][0])

    @property
    @lru_cache(maxsize=1)
    def name(self) -> str:
        "get the streams name as str"
        return self._stream["info"]["name"][0]

    @property
    @lru_cache(maxsize=1)
    def type(self) -> str:
        "get the streams type as str"
        return self._stream["info"]["type"][0]

    @property
    @lru_cache(maxsize=1)
    def channel_format(self) -> str:
        "get the streams data format as str"
        return self._stream["info"]["channel_format"][0]

    @property
    @lru_cache(maxsize=1)
    def created_at(self):
        "get the time stamp from when the channel was created as float"
        return float(self._stream["info"]["created_at"][0])

    @property
    def time_series(self) -> ndarray:
        "get the time_series of the stream, i.e its data as ndarray"
        return self._stream["time_series"]

    @property
    def time_stamps(self) -> ndarray:
        "get the time_stamps for each sample as ndarray"
        return self._stream["time_stamps"]


# -----------------------------------------------------------------------------
def XDFFile(filename: Union[Path, str]) -> Dict[str, XDFStream]:
    """load an :code:`xdf`-file and return a dictionary of its streams

    args
    ----
    filename: 
        the name of the xdffile

    returns
    -------
    streams: Dict[str, XDFStream]
        a collection of all :class:`~.XDFStream` s in the file. These can be indexed by their respective name

    """
    streams, _ = pyxdf.load_xdf(filename=str(filename))
    collection: Dict[str, XDFStream] = dict()
    for stream in streams:
        print("Parsing ", stream["info"]["name"][0])
        x = XDFStream(stream)
        collection[x.name] = x
    return collection
