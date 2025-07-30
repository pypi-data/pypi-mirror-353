from .gui_parser import gui_parser
from ..cookies import read_cookie_files
from ..gui import run_gui
from ..Provider import ProviderUtils

import buggpt.cookies
import buggpt.debug

def run_gui_args(args):
    if args.debug:
        buggpt.debug.logging = True
    if not args.ignore_cookie_files:
        read_cookie_files()
    host = args.host
    port = args.port
    debug = args.debug
    buggpt.cookies.browsers = [buggpt.cookies[browser] for browser in args.cookie_browsers]
    if args.ignored_providers:
        for provider in args.ignored_providers:
            if provider in ProviderUtils.convert:
                ProviderUtils.convert[provider].working = False

    run_gui(host, port, debug)

if __name__ == "__main__":
    parser = gui_parser()
    args = parser.parse_args()
    run_gui_args(args)
