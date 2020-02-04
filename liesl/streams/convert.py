# -*- coding: utf-8 -*-
"""
Convert streams
---------------
"""
from liesl.streams._xmltodict import parse as xml_to_dict
from typing import Dict
from pylsl import StreamInlet

ChannelIndexMap = Dict[str, int]  #: A Mapping from channel-names to channel-indices
# %%
def inlet_to_dict(inlet: StreamInlet) -> dict:
    """convert inlet information into a dictionary

    args
    ----
    inlet: pylsl.StreamInlet
        the inlet to convert into a dictionary


    returns
    -------
    
    output: dict
        a dictionary of key information parsed from the xml


    Example::

        import liesl
        stream = liesl.open_stream()
        d = liesl.inlet_to_dict(stream)

    """
    return streaminfoxml_to_dict(inlet.info().as_xml())


def get_channel_map(inlet: StreamInlet) -> ChannelIndexMap:
    """convert inlet information into a ChannelMapping
    
  
    args
    ----
    inlet: pylsl.StreamInlet
        the inlet to convert into a dictionary


    returns
    -------
    output: Dict[str, int]
        a dictionary mapping channel names to indices


    Example::

        import liesl
        stream = liesl.open_stream()
        chanmap = liesl.get_channel_map(stream)


    """
    info = inlet_to_dict(inlet)
    labels = {}
    for chan in info["desc"]["channels"]["channel"]:
        labels[chan["label"]] = chan["idx"]
    return labels


def streaminfoxml_to_dict(xml: str) -> dict:
    """
    args
    ----
    xml: str
        for example from xml = streaminlet.info().as_xml()
        
    returns
    -------
    
    output: dict
        a dictionary of key information parsed from the xml
    """
    output = dict(xml_to_dict(xml)["info"])
    try:
        desc = output["desc"]
    except KeyError:  # pragma: no cover
        return None

    output["desc"] = dict(desc)
    output["desc"]["channels"] = dict(output["desc"]["channels"])
    channels = output["desc"]["channels"]["channel"]
    if type(channels) == list:
        for idx, chan in enumerate(channels):
            tmp = dict(chan)
            tmp["idx"] = idx
            output["desc"]["channels"]["channel"][idx] = tmp
    else:
        tmp = dict(channels)
        tmp["idx"] = 0
        output["desc"]["channels"]["channel"] = [tmp]

    return output

