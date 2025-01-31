
# help.py
#
# GNXEdit menu handler
#
# Copyright 2024 gary-1959
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import common
import re
import os
from exceptions import GNXError
import webbrowser

from PySide6.QtWidgets import QMessageBox, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

hinclude = range(3, 10)     # include h3 to h9
toc_count = 0
tocs = {}

def tocfunc(match):
    global toc_count
    g0 = match.group(0)
    g1 = match.group(1)
    g2 = match.group(2)
    if int(g1) in hinclude:
        a = f"<a name=\"{g2.lower().replace(" ", "-")}\"><h{g1}>{g2}</h{g1}></a>"
        tocs[toc_count] = {"text": g2, "depth": g1, "href": f"{g2.lower().replace(" ", "-")}"}
        toc_count += 1
    else:
        a = g0
    return a


def get_help():

    subs = ["APP_TITLE", "APP_VERSION", "APP_LICENSE", "APP_LICENSE_LINK", "APP_COPYRIGHT", 
            "APP_VERSION_TEXT", "APP_GITHUB_LINK", "APP_SUBTITLE", "APP_DOC_PATH", "TOC"]

    try:
        path = os.path.join(os.path.dirname(__file__), "help.html")
        f = open(path, "r")
        help = f.read()
        f.close()

        # build toc based on <h*> tags
        regex = r"<h(\d)>(.+)<.+>"
        help = re.sub(regex, tocfunc, help, 0, re.MULTILINE | re.IGNORECASE)
        pass


        TOC = "<ul class='toc'>\n"
        for k, t in tocs.items():
            TOC += f"<li><a href='#{t["href"]}'>{t["text"]}</a></li>\n"

        TOC += "</ul>"
        
        # substitute {globals}
        for s in subs:
            help = help.replace("{" + s + "}", getattr(common, s) if hasattr(common, s) else eval(s))


        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tmp/", "help.html"))
        f = open(path, "w")
        f.write(help)
        f.close()

        webbrowser.open(f"file://{path}", new=1, autoraise = True)

    except Exception as e:
        e = GNXError(icon = QMessageBox.Critical, title = "Help File Error", \
                                                text = f"Unable to open help file.\n{e}", \
                                                buttons = QMessageBox.Ok)
        e.alert(common.APP_WINDOW)
