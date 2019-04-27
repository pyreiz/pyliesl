# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 13:35:12 2018

Robert Guggenberger
"""
import pylsl as lsl
# %%
def open_stream(**kwargs) -> lsl.StreamInlet:
    return lsl.StreamInlet(find_stream(**kwargs))

def find_stream(**kwargs) -> lsl.StreamInfo:                
    args = []
    for k, v in kwargs.items():
        args.append(f"{k}='{v}'")        
    if len(args)>0:
        logger.debug(f'Looking for {args}')
    
    # find all available streams, check whether they are fitting with kwargs
    available_streams = lsl.resolve_streams()        
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
    
    if len(fitting_streams)==0:
        raise TimeoutError('No streams found')
        
    if len(fitting_streams)==1:
        logger.info('Only one is available. Selecting this one:')
        logger.info((fitting_streams[0].as_xml()))
        return fitting_streams[0]
    
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