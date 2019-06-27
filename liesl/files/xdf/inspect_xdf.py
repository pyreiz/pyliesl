from pyxdf import load_xdf
from collections import Counter
from liesl.show.textplot import plot_crude as plot
# %%
def main(filename):    
    streams, info = load_xdf(filename)
    hdr = "XDF Fileversion " + info["info"]["version"][0]
    print(f"\r\nLoading {filename:3}\n")
    print(f"{hdr:>80}\n")
    line = "{0:<30s}{1:^7s}{2:^5s}{3:^5s}{4:>33s}"
    print(line.format("Name","Type", "Chans", "Fs", "Source"))
    print('-'*80)
    for s in streams:   
        name = s["info"]["name"][0]
        typ = s["info"]["type"][0]  
        cc = s["info"]["channel_count"][0]  
        sid = s["info"]["source_id"][0]  
        fs = s["info"]["nominal_srate"][0]
        print(line.format(name, typ, cc, fs, sid))
    
    print("\n\n")
    
    line = "{0:<30s}{1:>50s}"
    for s in streams:   
        typ = s["info"]["type"][0]  
        name = s["info"]["name"][0]
        if "marker" in typ.lower():
            events = Counter([s[0] for s in s["time_series"]])         
            print(line.format(name, "Events"))
            print('-'*80)
            for key, val in events.items():
                print("{0}{1:>{align}}".format(key, val, align=80-len(key)))
            
            print()
        else:
            print(line.format(name, "Exemplary data"))
            print('-'*80)
            x = s["time_stamps"]
            y = s["time_series"][:,0]
            plot(y, x)
            print()
if __name__ == "__main__":
    import sys
    main(sys.argv[1])
    input()
    