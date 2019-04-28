# -*- coding: utf-8 -*-
"""
Parse lsl xml and return a dictionary
Robert Guggenberger
"""
from liesl.tools._xmltodict import parse as xml_to_dict
# %%
def inlet_to_dict(inlet):
    '''
    args
    ----
    inlet: pylsl.StreamInlet
        for example from inlet = pyliesl.tools.streams.open_stream(type='EEG')
        
    returns
    -------
    
    output: dict
        a dictionary of key information parsed from the xml
    '''
    return streaminfoxml_to_dict(inlet.info().as_xml())
    
def streaminfoxml_to_dict(xml:str):
    '''
    args
    ----
    xml: str
        for example from xml = streaminlet.info().as_xml()
        
    returns
    -------
    
    output: dict
        a dictionary of key information parsed from the xml
    '''
    output = dict(xml_to_dict(xml)['info'])                          
    try:
        desc = output['desc']                
    except KeyError:
        desc = None

    if desc is not None:
        output['desc'] = dict(desc)
        output['desc']['channels'] = dict(output['desc']['channels'])
        channels = output['desc']['channels']['channel']
        if type(channels) == list:
            for idx, chan in enumerate(channels):
                tmp = dict(chan)
                tmp['idx'] = idx
                output['desc']['channels']['channel'][idx] = tmp               
        else:
            tmp  = dict(channels)
            tmp['idx'] = 0
            output['desc']['channels']['channel'] = [tmp]
    
    return output  