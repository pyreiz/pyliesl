# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 16:48:56 2019

@author: Robert Guggenberger
"""


def get_args():
    import argparse    
    parser = argparse.ArgumentParser(prog='liesl')
    subparsers = parser.add_subparsers(dest="subcommand")
    
    helpstr = """initialize the lsl_api.cfg for all users with system,
                globally for this user with global or 
                locally in this folder with local"""
    
    parser_cfg = subparsers.add_parser('config', help=helpstr)        
    parser_cfg.add_argument('init', action="store_true", help=helpstr)
    parser_cfg.add_argument('--system', action="store_true", help="system-wide")
    parser_cfg.add_argument('--global', dest="_global", action="store_true", help="global")
    parser_cfg.add_argument('--local', action="store_true", help="local")
    
    
    helpstr = """list available LSL streams"""
    parser_cfg = subparsers.add_parser('list', help=helpstr)        
    parser_cfg.add_argument('--field', help="which field to print", 
                            default="any")
    

    helpstr = """Visualize a specific LSL streams"""
    parser_cfg = subparsers.add_parser('show', help=helpstr)    
    parser_cfg.add_argument('--name', help="name of the stream")
    parser_cfg.add_argument('--type', help="type of the stream")
    parser_cfg.add_argument('--channel', help="which channel to visualize", type=int)
    parser_cfg.add_argument('--textplot', action="store_true", 
                            help="whether to use textplot or mpl")
    
    helpstr = """mock a LSL stream"""
    parser_cfg = subparsers.add_parser('mock', help=helpstr)    
    parser_cfg.add_argument('--name', help="name of the stream", 
                            default="Liesl-Mock")
    parser_cfg.add_argument('--type', help="type of the stream",
                            default="EEG")
    parser_cfg.add_argument('--channel_count', help="number of channels",
                            type=int, default=8)
    return parser.parse_known_args()
                   
def main():
    args, unknown = get_args()
    #print(args)
    if args.subcommand == "config":
       if args.init:
            from liesl.cli.lsl_api import init_lsl_api_cfg
            if args.system:
                init_lsl_api_cfg("system")
            if args._global:
                init_lsl_api_cfg("global")
            if args.local:
                init_lsl_api_cfg("local")
       return
   
    if args.subcommand == "show":
        kwargs = vars(args)        
        if args.textplot:
            from liesl.show.textplot import main            
            kwargs["channel"] = kwargs.get("channel", 0)
        else:
            from liesl.show.mpl import main        
            
        del kwargs["subcommand"]
        del kwargs["textplot"]        
        arguments = dict()
        for k,v in kwargs.items():
            if v is not None:
                arguments[k] = v
        main(**arguments)
        return
    
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
    
    if args.subcommand == "list":
        
        from liesl.streams.finder import available_streams        
        if args.field == "any":
            available_streams()
        else:
            streams = available_streams(do_print=False)
            for a in streams:
                print(getattr(a, args.field)())
        
        return
    
if __name__ == '__main__':
    get_args()
