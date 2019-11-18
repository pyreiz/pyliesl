from pyxdf import load_xdf
from collections import Counter
from array import array
from math import floor
import textwrap
# %%


def linspace(a, b, n=80):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [int(diff * i + a) for i in range(n)]


def plot(y, x=None, width=80, height=10):
    """Print a crude ASCII art plot"""
    y_raw = y.copy()

    if x is None:
        x_raw = [x for x in range(len(y))]
    else:
        x_raw = x.copy()

    if len(x_raw) != len(y_raw):
        raise ValueError("Unequal len of x and y")

    # smoothen and downsample because we have only <width> char available and
    # too many samples cause aliasing and outlier issues
    if len(y_raw) > width * 100:
        step = len(y_raw)//79
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
    b = max(x_raw)
    # Normalize height to screen space

    x = linspace(0, len(x_raw)-1, width)

    if ma == mi:
        if ma:
            mi, ma = sorted([0, 2*ma])
        else:
            mi, ma = -1, 1

    y = []
    for ix in x:
        new_y = (y_raw[ix] - mi) / (ma - mi)
        new_y = floor(new_y * (height-1))
        y.append(new_y)

    canvas = []
    for lix in range(height):
        line = array('u', ' '*width)
        canvas.append(line)

    def put(canvas, xpos, ypos, symbol):
        canvas[len(canvas)-ypos-1][xpos] = symbol

    for xix, (pre, val, post) in enumerate(zip([y[0]]+y, y, y[1:]+[y[-1]])):
      #  canvas[val][xix] = '─'
        if val < post:
            for l in range(val, post):
                put(canvas, xix, l, "│")
            put(canvas, xix, post, "╭")
            put(canvas, xix, val, "╯")
        if val > post:
            for l in range(post, val):
                put(canvas, xix, l, "│")
            put(canvas, xix, post, "╰")
            put(canvas, xix, val, "╮")
        if val == post:
            put(canvas, xix, val, '─')

    for line in canvas:
        print(line.tounicode())

    bottom = ""
    bottom += "{:<{width}g}".format(a, width=(width//2)-3)
    bottom += ("{:^5g}".format((a + b)/2))  # .ljust(width//2)
    bottom += "{:>{width}g}".format(b, width=(width//2)-2)
    print(bottom)


def shorten(text: str, width: int, placeholder="..."):
    if len(text) <= width:
        return text
    else:
        return textwrap.wrap(text, width-len(placeholder))[0] + placeholder


def load_concise(filename: str):
    from pyxdf import resolve_streams
    print(f"\r\nLoading {filename:3}\n")
    line = "{0:<25s}{1:^20s}{2:4s}{3:^5s}{4:>26s}"
    print(line.format("Name", "Type", "Ch", "Fs", "Source"))
    print('-'*80)
    sinfos = resolve_streams(filename)
    for sinfo in sinfos:
        name = sinfo["name"]
        typ = sinfo["type"]
        cc = sinfo["channel_count"]
        fs = sinfo["nominal_srate"]
        name = shorten(name, 25)
        typ = shorten(typ, 20)
        try:
            sid = sinfo["source_id"]
            if sid is None:
                sid = "Unknown"
            sid = shorten(sid, 25)
        except IndexError:
            sid = '\"\"'

        print(line.format(name, typ, str(cc), str(fs), sid))

    print("\n")


def main(filename):
    streams, info = load_xdf(filename)
    hdr = "XDF Fileversion " + info["info"]["version"][0]
    print(f"\r\nLoading {filename:3}\n")
    print(f"{hdr:>80}\n")
    line = "{0:<25s}{1:^20s}{2:4s}{3:^5s}{4:>26s}"
    print(line.format("Name", "Type", "Ch", "Fs", "Source"))
    print('-'*80)
    for s in streams:
        name = s["info"]["name"][0]
        typ = s["info"]["type"][0]
        cc = s["info"]["channel_count"][0]
        fs = s["info"]["nominal_srate"][0]
        name = shorten(name, 25)
        typ = shorten(typ, 20)
        try:
            sid = s["info"]["source_id"][0]
            sid = shorten(sid, 25)
        except IndexError:
            sid = '\"\"'

        print(line.format(name, typ, cc, fs, sid))

    print("\n")

    line = "{0:<30s}{1:>50s}"
    for s in streams:
        typ = s["info"]["type"][0]
        name = s["info"]["name"][0]
        if "marker" in typ.lower():
            events = Counter([s[0] for s in s["time_series"]])
            print(line.format(name, "Events"))
            print('-'*80)
            for key, val in events.items():
                if key == "":
                    wrapped_key = '\"\"'
                else:
                    wrapped_key = textwrap.shorten(key, width=70,
                                                   placeholder="...")
                alignment = 80-len(wrapped_key)
                print("{0}{1:>{align}}".format(wrapped_key,
                                               val, align=alignment))

            print()
        else:
            print(line.format(name, "Exemplary data"))
            print('-'*80)
            sz = s["time_series"].shape
            if sz[1]:
                x = s["time_stamps"]
                y = s["time_series"][:, 0]
                plot(y, x)
            else:
                print("No data found, array has shape({0}, {1})".format(*sz))
            print()

    print(f"Overview finished for {filename:3}\n")


if __name__ == "__main__":
    #import sys
    # main(sys.argv[1])
    # input()
    import random
    random.seed(1)
    y = [random.random() for y in range(0, 100, 1)]
