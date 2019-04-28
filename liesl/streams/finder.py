# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 13:35:12 2018

Robert Guggenberger
"""
import pylsl
# %%
def open_stream(**kwargs) -> pylsl.StreamInlet:
    return pylsl.StreamInlet(select_from_available_streams(**kwargs))

def available_streams():
    available_streams = pylsl.resolve_streams()
    for a in available_streams:
        print(a.as_xml())
        
def select_from_available_streams(**kwargs) -> pylsl.StreamInfo:   
    '''try to find the stream based on the kwargs,
    if more than one were found, interactively select one
    '''             
    fitting_streams = find_streams(**kwargs)
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

def find_streams(**kwargs) -> pylsl.StreamInfo:        
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
    del available_streams
    
    # either throws a timepout, returns a streaminfo or a list of streaminfos
    if len(fitting_streams)==0:
        raise TimeoutError('No streams found')
        
    if len(fitting_streams)==1:
        return fitting_streams[0]
    
    else:
        return fitting_streams 