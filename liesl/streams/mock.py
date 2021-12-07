#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:15:38 2019

@author: Robert Guggenberger

"""

import time
from random import random as rand
from random import choice
from pylsl import StreamInfo, StreamOutlet, local_clock
import threading
from math import sin, pi


# %%
class Mock(threading.Thread):
    def __init__(
            self,
            name="Liesl-Mock-EEG",
            type="EEG",
            channel_count=8,
            nominal_srate=1000,
            channel_format="float32",
            source_id=None,
    ):

        threading.Thread.__init__(self)

        if source_id == None:
            source_id = str(hash(self))

        self.info = StreamInfo(
            name, type, channel_count, nominal_srate, channel_format, source_id
        )
        self.channel_count = channel_count
        self.samplestep = 1 / nominal_srate
        self.is_running = False
        channels = self.info.desc().append_child("channels")
        types = (f"MockEEG" for x in range(1, channel_count + 1, 1))
        units = ("au" for x in range(1, channel_count + 1, 1))
        names = (f"C{x:03d}" for x in range(1, channel_count + 1, 1))
        for c, u, t in zip(names, units, types):
            channels.append_child("channel").append_child_value(
                "label", c
            ).append_child_value("unit", u).append_child_value("type", t)

    def stop(self):
        self.is_running = False
        self.join()
        print("Shutting down")

    def await_running(self):
        try:
            self.start()
        except RuntimeError:
            pass
        while not self.is_running:
            pass

    def run(self):
        outlet = StreamOutlet(self.info)
        count = 0.0
        print("now sending data...")
        self.is_running = True
        while self.is_running:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            # mysample = [rand() for c in range(self.channel_count)]
            mysample = []

            for c in range(self.channel_count):
                if c == 0:
                    mysample.append(rand())
                else:
                    smpl = sin((c ** 2) * 2 * pi * count * self.samplestep)
                    mysample.append(smpl)
            count += 1.0
            # now send it and wait for a bit
            outlet.push_sample(mysample)
            time.sleep(self.samplestep)

    def __str__(self):
        return self.info.as_xml()


def _streams_to_string(streams_as_dict):
    output = ""
    for idx, stream in enumerate(streams_as_dict):
        output += f"{stream}, "
    return output[:-2]


def stream_from_file(file, streamname=None):
    from pyxdf import load_xdf
    from pylsl import StreamInfo
    streams, i = load_xdf(file)
    print(f"Loaded file {file}")
    streams_as_dict = {}
    for ix, stream in enumerate(streams):
        streamname_from_recorded = stream['info']['name'][0]
        streams_as_dict[streamname_from_recorded] = stream
    if streamname is None:
        while True:
            print("Select a stream")
            stream_idx_pairs = {}
            for idx, stream in enumerate(streams_as_dict):
                stream_idx_pairs[idx] = stream
                print(f"[{idx}] {stream}")
            try:
                index = int(input(f"Select a stream from 0-{len(stream_idx_pairs) - 1}: "))
                if index > 0 and index < len(stream_idx_pairs):
                    break
                else:
                    print("\Index is not in the correct range.")
                    continue
            except ValueError:
                print("\nPlease input an integer")
                continue
        streamname = stream_idx_pairs[index]

    try:
        stream = streams_as_dict[streamname]
    except KeyError:
        raise KeyError(f"Stream with name {streamname} not found. Available are {_streams_to_string(streams_as_dict)}")
    info = stream["info"]
    streaminfo = StreamInfo(
        name="Recorded-Mock-EEG",
        type=info["type"][0],
        channel_count=int(info["channel_count"][0]),
        nominal_srate=float(info["nominal_srate"][0]),
        channel_format=info["channel_format"][0],
        source_id=info["source_id"][0]
    )
    return stream, streaminfo


class RecordedMock(threading.Thread):
    def __init__(
            self,
            stream,
            info
    ):
        self.info = info
        self.stream = stream
        channel_count = self.stream['time_series'].shape[1]
        channels = self.info.desc().append_child("channels")
        types = (f"MockEEG" for x in range(1, channel_count + 1, 1))
        units = ("au" for x in range(1, channel_count + 1, 1))
        names = (f"C{x:03d}" for x in range(1, channel_count + 1, 1))
        for c, u, t in zip(names, units, types):
            channels.append_child("channel").append_child_value(
                "label", c
            ).append_child_value("unit", u).append_child_value("type", t)
        threading.Thread.__init__(self)

    def stop(self):
        self.is_running = False
        self.join()
        print("Shutting down")

    def await_running(self):
        try:
            self.start()
        except RuntimeError:
            pass
        while not self.is_running:
            pass

    def run(self):
        outlet = StreamOutlet(self.info)
        count = 0
        print("[Mock] now sending data...")
        self.is_running = True
        timestamps = self.stream['time_stamps']
        timeseries = self.stream['time_series']
        num_of_samples = len(timestamps)

        while self.is_running:
            smpl = timeseries[count % num_of_samples]
            count += 1
            # now send it and wait for a bit
            outlet.push_sample(smpl)
            time_diff = timestamps[(count + 1) % num_of_samples] - timestamps[count % num_of_samples]
            if time_diff > 0:
                time.sleep(time_diff)
            else:
                time.sleep(0.001)

    def __str__(self):
        return self.info.as_xml()


class MarkerMock(Mock):
    def __init__(
            self,
            name="Liesl-Mock-Marker",
            type="Marker",
            channel_count=1,
            nominal_srate=0,
            channel_format="string",
            source_id=None,
            markernames=["Test", "Blah", "Marker", "XXX", "Testtest", "Test-1-2-3"],
    ):

        threading.Thread.__init__(self)

        if source_id == None:
            source_id = str(hash(self))

        self.info = StreamInfo(
            name, type, channel_count, nominal_srate, channel_format, source_id
        )
        self.channel_count = channel_count
        self.markernames = markernames

    def generate_marker(self):
        while True:
            yield [choice(self.markernames)]

    def run(self):
        self.is_running = True
        print("now sending data...")
        outlet = StreamOutlet(self.info)
        markers = self.generate_marker()
        while self.is_running:
            sample = next(markers)
            tstamp = local_clock()
            print(f"Pushed {sample} at {tstamp}")
            outlet.push_sample(sample, tstamp)
            time.sleep(rand())
