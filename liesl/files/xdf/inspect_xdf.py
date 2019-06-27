from pyxdf import load_xdf
from collections import Counter
# %%
def linspace(a, b, n=80):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [int(diff * i + a) for i in range(n)]
    
def plot(y, x=None, width=80, height=18):
    """Print a crude ASCII art plot"""
    y_raw = y.copy()    
    
    if x is None:
        x_raw = [x for x in range(len(y))]
    else:
        x_raw = x.copy()    
        
    if len(x_raw) != len(y_raw):
        raise ValueError("Unequal len of x and y")
    
    # smoothen because heavy aliasing and outlier issues
    if len(y_raw) > 80 *100: 
        step  = len(y_raw)//79
        smooth_y = []
        smooth_x = []
        for ixa, ixb in zip(range(0, len(y_raw)-step, step),
                            range(step, len(y_raw), step)):
            smooth_y.append(sum(y_raw[ixa:ixb])/step)
            smooth_x.append(x[ixa])    
        smooth_x[-1] = max(x_raw)
        smooth_x[0] = min(x_raw)
        y_raw = smooth_y
        x_raw = smooth_x
            

    ma = max(y_raw)    
    mi = min(y_raw)
    
    a = min(x_raw)
    b =  max(x_raw)
    # Normalize height to screen space
    
    x = linspace(0, len(x_raw)-1, width)        
        
    if ma == mi:
        if ma:
            mi, ma = sorted([0, 2*ma])
        else:
            mi, ma = -1, 1
            
    y = []        
    for ix in x:
        new_y = int(float(height)*(y_raw[ix] - mi)/(ma - mi))
        y.append(new_y) 
        
    margin = 0 # space left for y-labels

    offset = 1/height
    for h in range(height - 1, -1, -1):
        s = [' '] * width
        for x in range(width):
            try:
                if y[x] == h:          
                    if  y[x - 1] < y[x] and  y[x+1] > y[x]:
                        s[x] = "╱"
                    elif y[x - 1] > y[x] and  y[x+1] < y[x]:
                        s[x] = "╲"
                    elif y[x - 1] > y[x] and  y[x+1] == y[x]:
                        s[x] = "╰"
                    elif y[x - 1] < y[x] and  y[x+1] == y[x]:
                        s[x] = "╭"         
                    elif y[x - 1] == y[x] and  y[x+1] > y[x]:
                        s[x] = "╯"
                    elif y[x - 1] == y[x] and  y[x+1] < y[x]:
                        s[x] = "╮"
                    elif y[x - 1] == y[x] and  y[x+1] == y[x]:
                        s[x] = '─'
                    elif y[x - 1] > y[x] and  y[x+1] > y[x]:
                        s[x] = "v"
                    elif y[x - 1] < y[x] and  y[x+1] < y[x]:
                        s[x] = "^"                    
                    else:
                        s[x] = "X"
                        
                if  y[x - 1] < y[x] and  y[x+1] > y[x]:
                    if h>y[x - 1] and h<y[x + 1]:
                        s[x] = "│"
                if y[x - 1] > y[x] and  y[x+1] < y[x]:
                    if h<y[x - 1] and h>y[x + 1]:
                        s[x] = "│"
                     
            except IndexError:
                if y[x] == h:   
                    s[x] = "-"

            #    if (x == 0 or y[x - 1] == h - 1) and (x == width - 1 or y[x + 1] == h + 1):
            #        s[x] = '/'
            #    elif (x == 0 or y[x - 1] == h + 1) and (x == width - 1 or y[x + 1] == h - 1):
            #        s[x] = '\\'
            #    else:
            #        s[x] = '.'

        s = "".join(s)
        #if h == height//2:
        #    s = s.replace(" ", "-")
        print(s)

    # Print x values
    bottom = ""
    offset = len("%g" % a)
    bottom += ("%g" % a).ljust(width//2 - offset)
    bottom += ("%g" % ((a + b)/2)).ljust(width//2)
    bottom += "%g" % b
    print(bottom)
    

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
    
