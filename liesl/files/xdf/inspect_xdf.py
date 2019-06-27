from pyxdf import load_xdf
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
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1])
    input()
    