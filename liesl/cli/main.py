# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 16:48:56 2019

@author: Robert Guggenberger
"""
import json


def get_args():
    import argparse
    parser = argparse.ArgumentParser(prog='liesl')
    subparsers = parser.add_subparsers(dest="subcommand")

    helpstr = """initialize the lsl_api.cfg for all users with system,
                globally for this user with global or
                locally in this folder with local"""

    # --------------------------------------------------------------------------
    parser_cfg = subparsers.add_parser('config', help=helpstr)
    helpstr = """system: /etc/lsl_api/lsl_api.cfg or
                          C:\\etc\\lsl_api\\lsl_api.cfg on Windows.\r\n
                 user: ~/lsl_api/lsl_api.cfg or
                          C:\\Users\\username\\lsl_api\\lsl_api.cfg on Windows.
                 local: lsl_api.cfg in the current working directory"""
    parser_cfg.add_argument('scope', choices=["system", "user", "local"],
                            help=helpstr)
    parser_cfg.add_argument('--default', action="store_true",
                            help="initializes a configuration from default")
    parser_cfg.add_argument('--sessionid', type=str,
                            help="sets the sessionid for this level")
    parser_cfg.add_argument('--knownpeers', type=str,
                            help="set knownpeers for this level")

    # -------------------------------------------------------------------------
    helpstr = """list available LSL streams"""
    parser_list = subparsers.add_parser('list', help=helpstr)
    parser_list.add_argument('--field', help="which field to print",
                             default="any")

    # -------------------------------------------------------------------------
    helpstr = """Visualize a specific LSL streams"""
    parser_show = subparsers.add_parser('show', help=helpstr)
    parser_show.add_argument('--name', help="name of the stream")
    parser_show.add_argument('--type', help="type of the stream")
    parser_show.add_argument(
        '--channel', help="which channel to visualize", type=int)
    parser_show.add_argument('--backend', choices=["mpl", "ascii"],
                             default="ascii", help="what backend to use")
    parser_show.add_argument('--frate', type=float,
                             default=20, help="at which frequency the plot will be updated")

    # -------------------------------------------------------------------------
    helpstr = """mock a LSL stream"""
    parser_mock = subparsers.add_parser('mock', help=helpstr)
    parser_mock.add_argument('--name', help="name of the stream",
                             default="Liesl-Mock")
    parser_mock.add_argument('--type', help="type of the stream",
                             default="EEG")
    parser_mock.add_argument('--channel_count', help="number of channels",
                             type=int, default=8)

    # -------------------------------------------------------------------------
    helpstr = """inspect an XDF file"""
    parser_xdf = subparsers.add_parser('xdf', help=helpstr)
    parser_xdf.add_argument('filename', help="filename")
    parser_xdf.add_argument('--count', type=int,
                            help="only peek into the file, looking for at most N streaminfos.")
    parser_xdf.add_argument('--timeout', type=float,
                            help="If searching takes too long, returns after timeout in seconds anyways. Useful for example if file is very large, and you are sure you started recording all streams at the beginnging, as this prevents parsing the whole file")

    return parser.parse_known_args(), parser


def start(args, unknown):

    # print(args)
    # -------------------------------------------------------------------------
    if args.subcommand == "xdf":
        if args.count or args.timeout:
            from liesl.files.xdf.inspect_xdf import load_concise as print_xdf
            print("Will search {0:3.2f} seconds to find at most {1:2.0f} streaminfos".format(
                args.timeout, args.count))
            print_xdf(args.filename, timeout=args.timeout, maxcount=args.count)
        else:
            from liesl.files.xdf.inspect_xdf import main as print_xdf
            print_xdf(args.filename)

    # -------------------------------------------------------------------------
    if args.subcommand == "config":
        if args.default:
            from liesl.cli.lsl_api import init_lsl_api_cfg
            init_lsl_api_cfg(args.scope)
            return

        from liesl.cli.lsl_api import Ini
        ini = Ini(args.scope)
        ini.refresh()
        if args.sessionid:
            print(args.sessionid)
            ini.ini["lab"]["SessionID"] = args.sessionid
            ini.write()

        if args.knownpeers:
            print(args.knownpeers)
            ini.ini["lab"]["KnownPeers"] = '{' + args.knownpeers + '}'
            ini.write()

        from liesl.cli.lsl_api import print_config
        print_config(args.scope)
        return

    # -------------------------------------------------------------------------
    if args.subcommand == "show":
        kwargs = vars(args)
        kwargs["channel"] = kwargs.get("channel", 0)
        if args.backend == "mpl":
            from liesl.show.mpl import main
        elif args.backend == "ascii":
            from liesl.show.textplot import main
        else:
            raise ValueError(f"Backend {args.backend} not available")

        del kwargs["backend"]
        del kwargs["subcommand"]
        arguments = dict()
        for k, v in kwargs.items():
            if v is not None:
                arguments[k] = v
        main(**arguments)
        return

    # -------------------------------------------------------------------------
    if args.subcommand == "mock":

        if "marker" in args.type.lower():
            from liesl.test.mock import MarkerMock
            m = MarkerMock(name=args.name,
                           type=args.type,
                           )
        else:
            from liesl.test.mock import Mock
            m = Mock(name=args.name,
                     type=args.type,
                     channel_count=args.channel_count)
        print(m)
        m.start()
        return
    # -------------------------------------------------------------------------
    if args.subcommand == "list":

        from liesl.streams.finder import available_streams
        if args.field == "any":
            available_streams()
        else:
            streams = available_streams(do_print=False)
            for a in streams:
                print(getattr(a, args.field)())

        return
    # -------------------------------------------------------------------------


def main():
    import sys
    (args, unknown), parser = get_args()
    start(args, unknown)
    sys.exit()


if __name__ == '__main__':

    get_args()
