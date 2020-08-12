"""
Peeking
-------
"""

from pyxdf import load_xdf
from collections import Counter
from typing import List, Dict
from liesl.show.textplot import zoom_plot as plot
import textwrap
from math import inf


def shorten(text: str, width: int, placeholder="..."):
    if len(text) <= width:
        return text
    else:
        return textwrap.wrap(text, width - len(placeholder))[0] + placeholder


def peek(filename: str, at_most=1, max_duration=10) -> List[Dict]:
    """peek into an xdf-file

    Find the first `at_most` N streaminfos of the xdf-file but do not search for longer that `max duration` seconds, whatever comes first.
    """
    from pyxdf.pyxdf import _read_varlen_int, parse_chunks, open_xdf
    from pyxdf.pyxdf import _parse_streamheader
    import struct
    import xml.etree.ElementTree as ET
    from math import inf
    from itertools import islice
    import time

    def _read_chunks(f, max_duration=10):
        t0 = time.time()
        while True:
            chunk = dict()
            try:
                chunk["nbytes"] = _read_varlen_int(f)
            except EOFError:
                return
            chunk["tag"] = struct.unpack("<H", f.read(2))[0]
            if chunk["tag"] == 2:
                chunk["stream_id"] = struct.unpack("<I", f.read(4))[0]
                xml = ET.fromstring(f.read(chunk["nbytes"] - 6).decode())
                chunk = {**chunk, **_parse_streamheader(xml)}
                yield chunk
            else:
                f.seek(chunk["nbytes"] - 2, 1)  # skip remaining chunk contents
            if time.time() - t0 > max_duration:
                return

    chunks = []
    with open_xdf(filename) as f:
        for chunk in islice(
            _read_chunks(f, max_duration=max_duration), at_most
        ):
            chunks.append(chunk)
    return parse_chunks(chunks)


def load_concise(filename: str, at_most=1, timeout: float = inf):
    print(f"\r\nLoading {filename:3} concisely\n")
    line = "{0:<25s}{1:^20s}{2:4s}{3:^5s}{4:>26s}"
    print(line.format("Name", "Type", "Ch", "Fs", "Source"))
    print("-" * 80)
    sinfos = peek(filename, at_most=at_most, max_duration=timeout)
    for sinfo in sinfos:
        name = sinfo["name"]
        typ = sinfo["type"]
        cc = sinfo["channel_count"]
        fs = sinfo["nominal_srate"]
        name = shorten(name, 25)
        typ = shorten(typ, 20)
        try:
            sid = sinfo["source_id"]
            sid = sid if sid else "Unknown"
            sid = shorten(sid, 25)
        except IndexError:
            sid = '""'

        print(line.format(name, typ, str(cc), str(fs), sid))

    print("\n")


def main(filename):
    print("main is deprecated, use load_fully instead")
    return load_fully(filename)


def load_fully(filename):

    print(f"\r\nLoading {filename:3} fully\n")
    streams, info = load_xdf(filename)
    hdr = "XDF Fileversion " + info["info"]["version"][0]
    print(f"{hdr:>80}\n")
    line = "{0:<25s}{1:^20s}{2:4s}{3:^5s}{4:>26s}"
    print(line.format("Name", "Type", "Ch", "Fs", "Source"))
    print("-" * 80)

    for s in streams:
        name = s["info"]["name"][0]
        typ = s["info"]["type"][0]
        cc = s["info"]["channel_count"][0]
        fs = float(s["info"]["nominal_srate"][0])
        fs = str(int(fs)) if int(fs) == fs else str(fs)
        name = shorten(name, 25)
        typ = shorten(typ, 20)
        try:
            sid = s["info"]["source_id"][0]
            # can be None in edge cases
            sid = sid if sid else "Unknown"
            sid = shorten(sid, 25)
        except IndexError:
            sid = '""'

        print(line.format(name, typ, cc, fs, sid))

    print("\n")

    line = "{0:<30s}{1:>50s}"
    for s in streams:
        typ = s["info"]["type"][0]
        name = s["info"]["name"][0]
        if "marker" in typ.lower():
            events = Counter([s[0] for s in s["time_series"]])
            print(line.format(name, "Events"))
            print("-" * 80)
            for key, val in events.items():
                if key == "":
                    wrapped_key = '""'
                else:
                    wrapped_key = textwrap.shorten(
                        key, width=70, placeholder="..."
                    )
                alignment = 80 - len(wrapped_key)
                print(
                    "{0}{1:>{align}}".format(wrapped_key, val, align=alignment)
                )

            print()
        else:
            print(line.format(name, "Exemplary data"))
            print("-" * 80)
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
    pass
