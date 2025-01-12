
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

from PySide6.QtWidgets import QMessageBox, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

def get_help():

    subs = ["APP_TITLE", "APP_VERSION", "APP_LICENSE", "APP_LICENSE_LINK", "APP_COPYRIGHT", 
            "APP_VERSION_TEXT", "APP_GITHUB_LINK", "APP_SUBTITLE"]

    try:
        path = os.path.join(os.path.dirname(__file__), "help.html")
        f = open(path, "r")
        help = f.read()
        f.close()
        # substitute {globals}
        for s in subs:
            regex = r"{" + s + "}"
            help = re.sub(regex, getattr(common, s), help, 0, re.MULTILINE)

        
        window = QMainWindow(common.APP_WINDOW)
        window.setWindowTitle("GNXEdit Help")
        window.resize(1025, 750)
        view = QWebEngineView(window)
        view.setHtml(help)
        window.setCentralWidget(view)
        window.show()

    except Exception as e:
        e = GNXError(icon = QMessageBox.Critical, title = "Help File Error", \
                                                text = f"Unable to open help file.\n{e}", \
                                                buttons = QMessageBox.Ok)
        e.alert(common.APP_WINDOW)
