# -*- coding: utf-8 -*-
"""
Command Line Interface
----------------------
"""
import json
import argparse
import sys
from math import inf
from ast import literal_eval


def get_parser():

    parser = argparse.ArgumentParser(prog="liesl")
    subparsers = parser.add_subparsers(dest="subcommand")

    # config ------------------------------------------------------------------
    helpstr = """initialize the lsl_api.cfg for all users with system,
                globally for this user with global or
                locally in this folder with local"""

    parser_cfg = subparsers.add_parser("config", help=helpstr)
    helpstr = """system: /etc/lsl_api/lsl_api.cfg or
                          C:\\etc\\lsl_api\\lsl_api.cfg on Windows.\r\n
                 user: ~/lsl_api/lsl_api.cfg or
                          C:\\Users\\username\\lsl_api\\lsl_api.cfg on Windows.
                 local: lsl_api.cfg in the current working directory"""
    parser_cfg.add_argument("scope", choices=["system", "user", "local"], help=helpstr)
    parser_cfg.add_argument(
        "--default",
        action="store_true",
        help="initializes a configuration from default",
    )
    parser_cfg.add_argument(
        "--sessionid", type=str, help="sets the sessionid for this level"
    )
    parser_cfg.add_argument(
        "--knownpeers", type=str, help="set knownpeers for this level"
    )

    # list --------------------------------------------------------------------
    helpstr = """list available LSL streams"""
    parser_list = subparsers.add_parser("list", help=helpstr)
    parser_list.add_argument(
        "--field",
        help="""which field to print. For example:    
                    liesl list --field '["name", "source_id"]'""",
        default="['any']",
        type=literal_eval,
    )

    # show --------------------------------------------------------------------
    helpstr = """Visualize a specific LSL streams"""
    parser_show = subparsers.add_parser("show", help=helpstr)
    parser_show.add_argument("--name", help="name of the stream")
    parser_show.add_argument("--type", help="type of the stream")
    parser_show.add_argument("--channel", help="which channel to visualize", type=int)
    parser_show.add_argument(
        "--backend",
        choices=["mpl", "ascii"],
        default="ascii",
        help="what backend to use",
    )
    parser_show.add_argument(
        "--frate",
        type=float,
        default=20,
        help="at which frequency the plot will be updated",
    )

    # mock --------------------------------------------------------------------
    helpstr = """mock a LSL stream"""
    parser_mock = subparsers.add_parser("mock", help=helpstr)
    parser_mock.add_argument("--type", help="type of the stream", default="EEG")

    # xdf ---------------------------------------------------------------------
    helpstr = """inspect an XDF file"""
    parser_xdf = subparsers.add_parser("xdf", help=helpstr)
    parser_xdf.add_argument("filename", help="filename")
    parser_xdf.add_argument(
        "-a",
        "--at-most",
        type=int,
        help="return lastest once that many streams were found, regardloss of how long it takes. Useful if file is very large, and can prevent parsing the whole file. defaults to sys.maxsize because integers are required, but unbound in python. Set it to 0' to load the file completely",
        default=sys.maxsize,
    )
    parser_xdf.add_argument(
        "-t",
        "--timeout",
        type=float,
        help="return latest after this many seconds, regardless of how many streams were found. Useful if the file is very large, and you are sure you started recording all streams at the beginnging, as this prevents parsing the whole file. defaults to 1 second. Set it to 'inf' to load the file completely",
        default=1,
    )

    return parser


def xdf(args):
    "execute xdf subcommand"
    from liesl.files.xdf.inspect_xdf import load_concise
    from liesl.files.xdf.inspect_xdf import load_fully

    if args.at_most == 0 or args.timeout == inf:
        load_fully(args.filename)
    else:
        load_concise(args.filename, args.at_most, args.timeout)


def config(args):
    "execute subcommand config"
    if args.default:
        from liesl.cli.lsl_api import init_lsl_api_cfg

        init_lsl_api_cfg(args.scope)
        return

    from liesl.cli.lsl_api import Ini

    ini = Ini(args.scope)
    ini.refresh()
    if args.sessionid:
        print(args.sessionid)
        try:
            ini.ini["lab"]["SessionID"] = args.sessionid
        except KeyError:
            ini.ini["lab"] = {}
            ini.ini["lab"]["SessionID"] = args.sessionid
        ini.write()

    if args.knownpeers:
        print(args.knownpeers)
        try:
            ini.ini["lab"]["KnownPeers"] = "{" + args.knownpeers + "}"
        except KeyError:
            ini.ini["lab"] = {}
            ini.ini["lab"]["KnownPeers"] = "{" + args.knownpeers + "}"
        ini.write()

    from liesl.cli.lsl_api import print_config

    print_config(args.scope)


def show(args):
    "execute subcommand show"
    kwargs = vars(args)
    kwargs["channel"] = kwargs.get("channel", 0)
    if args.backend == "mpl":
        from liesl.show.mpl import show
    elif args.backend == "ascii":
        from liesl.show.textplot import show

    del kwargs["backend"]
    del kwargs["subcommand"]
    arguments = dict()
    for k, v in kwargs.items():
        if v is not None:
            arguments[k] = v
    return show(**arguments)


def mock(args):
    "execute subcommand mock"
    if "marker" in args.type.lower():
        from liesl.streams.mock import MarkerMock

        m = MarkerMock()
    else:
        from liesl.streams.mock import Mock

        m = Mock()
    print(m)
    m.start()


def do_list(args):
    "execute subcommand list"
    if args.field == ["any"]:
        from liesl.streams.finder import print_available_streams

        return print_available_streams()
    else:
        pass
        from liesl.streams.finder import print_available_streams_fields

        return print_available_streams_fields(args.field)


def start(args, unknown):
    if args.subcommand == "xdf":
        return xdf(args)
    if args.subcommand == "config":
        return config(args)
    if args.subcommand == "show":
        return show(args)
    if args.subcommand == "mock":
        return mock(args)
    if args.subcommand == "list":
        return do_list(args)


def main():
    "entry point for console_scripts: liesl"
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    start(args, unknown)


def format_help(parser) -> str:  # pragma no cover
    cb = ".. code-block:: none\n\n"

    title = parser.prog + "\n" + "~" * len(parser.prog)
    helpstr = parser.format_help()
    yield title + "\n"
    yield cb
    for line in helpstr.splitlines():
        yield "   " + line + "\n"
    yield "\n\n"
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for choice, subparser in action.choices.items():
                title = subparser.prog + "\n" + "~" * len(subparser.prog)
                yield title + "\n"
                yield cb
                for line in subparser.format_help().splitlines():
                    yield "   " + line + "\n"
                yield "\n\n"


def create_cli_rst(fname: str):  # pragma no cover
    desc = """
   
liesl also offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. create a mock LSL outlet producing fake EEG with    

.. code-block:: bash

   liesl mock --type EEG

"""
    helpstr = format_help(get_parser())
    with open(fname, "w") as f:
        f.write("liesl CLI\n")
        f.write("---------\n")
        f.write(desc)
        for h in helpstr:
            f.write(h)

