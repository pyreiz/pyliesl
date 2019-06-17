# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 13:35:12 2018

Robert Guggenberger
"""
import pylsl
# %%
def get_info(stream):
    info = stream.info()
    return pylsl.StreamInfo(name=info.name(), 
                            type=info.type(), 
                            channel_count=info.channel_count(),
                            nominal_srate=info.nominal_srate(),
                            channel_format=info.channel_format(),
                            source_id=info.source_id())

def open_stream(**kwargs) -> pylsl.StreamInlet:
    return pylsl.StreamInlet(select_from_available_streams(**kwargs))

def open_streams(**kwargs) -> pylsl.StreamInlet:
    streams = []
    for inlet in available_fitting_streams(**kwargs):
        streams.append(pylsl.StreamInlet(inlet))
    return streams

def available_streams(do_print=True):
    available_streams = pylsl.resolve_streams()
    if do_print:
        for a in available_streams:
            print(a.as_xml())
    return available_streams
        
def select_from_available_streams(**kwargs) -> pylsl.StreamInfo:   
    '''try to find the stream based on the kwargs,
    if more than one were found, interactively select one
    '''             
    fitting_streams = find_fitting_streaminfos(**kwargs)
    if type(fitting_streams) is pylsl.StreamInfo:
        return fitting_streams
    else:
        print('Several available. Select one ')        
        try:
            while True:
                print('----------------start of avaible streams---------------')
                for cnt, s in enumerate(fitting_streams):
                    x = ''            
                    print(s.as_xml())
                    while not x in ['Y','N','C']:
                        x = input('Choose this [Y/N/C] ').upper()
                        
                    if x == 'N':
                        continue 
                    elif x == 'Y':
                        return s
                    elif x == 'C':
                        raise ConnectionRefusedError()
        except ConnectionRefusedError:
            print('You cancelled the connection attempt')
            return None 

def available_fitting_streams(**kwargs):
    '''
    args
    ----
    **kwargs:
        keyword arguments to identify the desired stream
        
    returns
    -------
    varies: {Exception, StreamInfo, List[Streaminfo,...]}
        if no stream was found, it raises a TimeoutError
        otherwise it either returns a streaminfo or a list of streaminfos
    
    '''       
    args = []
    for k, v in kwargs.items():
        args.append(f"{k}='{v}'")        
    
    # find all available streams, check whether they are fitting with kwargs
    available_streams = pylsl.resolve_streams()        
    if len(available_streams)==0:
        raise TimeoutError('No streams found')
    else:
        fitting_streams = []
        for st in available_streams:
            for k, v in kwargs.items():
                if eval('st.'+k+'()') != v:
                    break
            else:
                fitting_streams.append(st)
    
    return fitting_streams

def find_fitting_streaminfos(**kwargs) -> pylsl.StreamInfo:        
    '''
    args
    ----
    **kwargs:
        keyword arguments to identify the desired stream
        
    returns
    -------
    varies: {Exception, StreamInfo, List[Streaminfo,...]}
        if no stream was found, it raises a TimeoutError
        otherwise it either returns a streaminfo or a list of streaminfos
    
    '''       
    args = []
    for k, v in kwargs.items():
        args.append(f"{k}='{v}'")        
    
    # find all available streams, check whether they are fitting with kwargs
    fitting_streams = available_fitting_streams(**kwargs)
    
    # either throws a timepout, returns a streaminfo or a list of streaminfos
    if len(fitting_streams)==0:
        raise TimeoutError('No streams found')
        
    if len(fitting_streams)==1:
        return fitting_streams[0]
    
    else:
        return fitting_streams 