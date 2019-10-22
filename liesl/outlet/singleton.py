import pylsl
from liesl import LOCALHOSTNAME
import weakref
# %%
class SingletonOutlet():
    "LSL based outlet as a singleton, to prevent zombie outlets"
    instances = weakref.WeakValueDictionary() 
    # weak value referenced, i.e. keys disappear when the value is gc-collected

    def __new__(cls, 
                name='default-singleton',
                type='singleton', 
                channel_count=1, 
                nominal_srate=0, 
                channel_format='string',
                source_id=None):
        
        if source_id is None:
            source_id = '-'.join((name, LOCALHOSTNAME))
        info = pylsl.StreamInfo(name, type=type,
                                channel_count=channel_count, 
                                nominal_srate= nominal_srate, 
                                channel_format=channel_format, 
                                source_id=source_id)
        
        key = hash(info.as_xml())   
        value =  cls.instances.get(key, None)                             
        if value is None:                                                
            print(f"Creating a new instance")          
            outlet = pylsl.StreamOutlet(info)
            outlet.info = info
            cls.instances[key] = outlet
        else:
            print(f"Reusing an old instance")
            outlet = value
        print(outlet.info.as_xml())  
        return outlet

    