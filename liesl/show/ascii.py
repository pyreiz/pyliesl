from math import floor
from array import array
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
