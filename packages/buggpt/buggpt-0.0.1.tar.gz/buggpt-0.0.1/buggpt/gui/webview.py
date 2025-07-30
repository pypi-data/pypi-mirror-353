from __future__ import annotations

import sys
import os.path
import webview
try:
    from platformdirs import user_config_dir
    has_platformdirs = True
except ImportError:
    has_platformdirs = False

from buggpt.gui.gui_parser import gui_parser
from buggpt.gui.server.js_api import JsApi
import buggpt.version
import buggpt.debug

def run_webview(
    debug: bool = False,
    http_port: int = None,
    ssl: bool = True,
    storage_path: str = None,
    gui: str = None
):
    if getattr(sys, 'frozen', False):
        dirname = sys._MEIPASS
    else:
        dirname = os.path.dirname(__file__)
    webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.create_window(
        f"buggpt - {buggpt.version.utils.current_version}",
        os.path.join(dirname, "client/index.html"),
        text_select=True,
        js_api=JsApi(),
    )
    if has_platformdirs and storage_path is None:
        storage_path = user_config_dir("buggpt-webview")
    webview.start(
        private_mode=False,
        storage_path=storage_path,
        debug=debug,
        http_port=http_port,
        ssl=ssl
    )

if __name__ == "__main__":
    parser = gui_parser()
    args = parser.parse_args()
    if args.debug:
        buggpt.debug.logging = True
    run_webview(args.debug, args.port, not args.debug)
