# -*- coding: utf-8 -*-
"""
Visualize data using matplotlib
-------------------------------
"""
import matplotlib.pyplot as plt
from liesl.api import open_streaminfo, RingBuffer


def show(**kwargs):
    if "channel" in kwargs:
        limit_channels = True
        channel = kwargs.get("channel")
        del kwargs["channel"]
    else:
        limit_channels = False

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
    buffer = RingBuffer(sinfo, duration_in_ms=1000)
    buffer.start()
    buffer.await_running()
    labels = []
    try:
        for cix, chan in enumerate(buffer.info["desc"]["channels"]["channel"]):
            if chan["label"] is not None:
                labels.append(chan["label"])
            else:
                labels.append(str(cix))
    except:
        for cix in range(int(buffer.info["channel_count"])):
            labels.append(str(cix))

    fig, ax = plt.subplots(1, 1)
    try:
        while plt.fignum_exists(fig.number):
            plt.pause(fsleep)
            ax.cla()
            chunks, tstamp = buffer.get()
            if limit_channels:
                ax.plot(tstamp, chunks[:, channel])
                ax.legend([labels[channel]], loc="upper left")
            else:
                ax.plot(tstamp, chunks)
                ax.legend(labels, loc="upper left")
    except KeyboardInterrupt:
        pass
    finally:
        buffer.stop()
        exit()
