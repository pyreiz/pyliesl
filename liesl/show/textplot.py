"""
Visualize data in the terminal
------------------------------
"""
from time import sleep
import os
from typing import List
from liesl.api import open_streaminfo, RingBuffer
from math import floor
from array import array


def cla():
    "clear the terminal"
    os.system("cls" if os.name == "nt" else "clear")


def linspace(a: int, b: int, n: int = 80) -> List[float]:
    "return a list of n evenly spaced values spanning from a to b"
    if n < 2:
        return b
    diff = (float(b) - a) / (n - 1)
    return [int(diff * i + a) for i in range(n)]


def plot(y: List[float], x: List[float] = None, width: int = 79, height: int = 18):
    """
    Print a crude ASCII art plot
    """
    y_raw = y.copy()
    width -= 6  # because of left margin
    if x is None:
        x_raw = [x for x in range(len(y))]
    else:
        x_raw = x.copy()

    if len(x_raw) != len(y_raw):
        raise ValueError("Unequal len of x and y")

    ma = max(y_raw)
    mi = min(y_raw)
    a = min(x_raw)
    b = max(x_raw)
    # Normalize height to screen space

    x = linspace(0, len(x_raw) - 1, width)

    if ma == mi:
        if ma:
            mi, ma = sorted([0, 2 * ma])
        else:
            mi, ma = -1, 1

    y = []
    for ix in x:
        new_y = int(float(height) * (y_raw[ix] - mi) / (ma - mi))
        y.append(new_y)

    for h in range(height - 1, -1, -1):
        s = [" "] * width
        for x in range(width):
            if y[x] == h:
                if (x == 0 or y[x - 1] == h - 1) and (
                    x == width - 1 or y[x + 1] == h + 1
                ):
                    s[x] = "/"
                elif (x == 0 or y[x - 1] == h + 1) and (
                    x == width - 1 or y[x + 1] == h - 1
                ):
                    s[x] = "\\"
                else:
                    s[x] = "."

        # Print y values
        if h == height - 1:
            prefix = "{0:4.1f}".format(ma)
        elif h == height // 2:
            prefix = "{0:4.1f}".format((mi + ma) / 2)
        elif h == 0:
            prefix = "{0:4.1f}".format(mi)
        else:
            prefix = " " * 4
        s = "".join(s)
        if h == height // 2:
            s = s.replace(" ", "-")
        print(prefix + " | " + s)

    # Print x values
    bottom = "  "
    bottom += "{0:<10.0f}".format(a[0])
    bottom += "{0:^58.1f}".format(((a + b) / 2)[0])
    bottom += "{0:>10.0f}".format(b[0])

    print(bottom)


def zoom_plot(y: List[float], x: List[float] = None, width: int = 80, height: int = 10):
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
        step = len(y_raw) // 79
        smooth_y = []
        smooth_x = []
        for ixa, ixb in zip(
            range(0, len(y_raw) - step, step), range(step, len(y_raw), step)
        ):
            smooth_y.append(sum(y_raw[ixa:ixb]) / step)
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

    x = linspace(0, len(x_raw) - 1, width)

    if ma == mi:
        if ma:
            mi, ma = sorted([0, 2 * ma])
        else:
            mi, ma = -1, 1

    y = []
    for ix in x:
        new_y = (y_raw[ix] - mi) / (ma - mi)
        new_y = floor(new_y * (height - 1))
        y.append(new_y)

    canvas = []
    for lix in range(height):
        line = array("u", " " * width)
        canvas.append(line)

    def put(canvas, xpos, ypos, symbol):
        canvas[len(canvas) - ypos - 1][xpos] = symbol

    for xix, (pre, val, post) in enumerate(zip([y[0]] + y, y, y[1:] + [y[-1]])):
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
            put(canvas, xix, val, "─")

    for line in canvas:
        print(line.tounicode())

    bottom = ""
    bottom += "{:<{width}g}".format(a, width=(width // 2) - 3)
    bottom += "{:^5g}".format((a + b) / 2)  # .ljust(width//2)
    bottom += "{:>{width}g}".format(b, width=(width // 2) - 2)
    print(bottom)


def show(**kwargs):

    if "channel" in kwargs:
        channel = kwargs.get("channel")
        del kwargs["channel"]
    else:
        channel = 0

    if "frate" in kwargs:
        frate = kwargs.get("frate")
        del kwargs["frate"]
    else:
        frate = 20

    fsleep = 1 / frate

    sinfo = open_streaminfo(**kwargs)
    if sinfo is None:
        print("No streams found")
        exit()
    duration = 80 * 1000 / sinfo.nominal_srate()
    buffer = RingBuffer(sinfo, duration_in_ms=duration)
    buffer.start()
    buffer.await_running()
    try:
        while buffer.is_running:
            sleep(fsleep)
            cla()
            chunk, tstamps = buffer.get()
            plot(chunk[:, channel], tstamps, width=79)
            sleep(fsleep)
    except KeyboardInterrupt:
        pass
    finally:
        buffer.stop()
        exit(0)
