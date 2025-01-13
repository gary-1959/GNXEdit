# common.py
#
# GNXEdit common file
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

import os

def init():
    global GNXEDIT_CONFIG, GNXEDIT_CONFIG_PATH, GNXEDIT_CONFIG_FILE, GNXEDIT_DATABASE_FILE, APP_VERSION, \
            APP_LICENSE, APP_LICENSE_LINK, APP_COPYRIGHT, APP_HELP_LINK, ABOUT_TEXT, APP_VERSION_TEXT, \
            APP_WINDOW, APP_TITLE, APP_GITHUB_LINK, APP_SUBTITLE, APP_DOC_PATH

    GNXEDIT_CONFIG = None
    GNXEDIT_CONFIG_FILE = None
    GNXEDIT_DATABASE_FILE = None
    GNXEDIT_CONFIG_PATH = None

    APP_VERSION = "1.0"
    APP_VERSION_DATE = "11 January, 2025"
    APP_VERSION_TEXT = f"Version: {APP_VERSION}, {APP_VERSION_DATE}"
    APP_COPYRIGHT = "Copyright &#169; 2025 Gary Barnes (gary-1959). All rights reserved."
    APP_LICENSE = "This software and its source code is made freely available under the GNU General Public License version 3."
    APP_LICENSE_LINK = "<a href='https://opensource.org/license/gpl-3-0'>https://opensource.org/license/gpl-3-0'</a>"
    APP_HELP_LINK = "https://github.com/gary-1959/GNXEdit"
    APP_GITHUB_LINK = "<a href='https://github.com/gary-1959/GNXEdit'>https://github.com/gary-1959/GNXEdit</a>"
    APP_TITLE = "GNXEdit"
    APP_SUBTITLE = "Editor and Librarian for Digitech GNX1"
    ABOUT_TEXT = f"<h1>{APP_TITLE}</h1>" + \
                        f"<h2>{APP_SUBTITLE}</h2>" + \
                        f"<p>{APP_VERSION_TEXT}</p><p>{APP_COPYRIGHT}</p>" + \
                        f"<p>{APP_LICENSE}</p><p>More details at: {APP_LICENSE_LINK}</p>" + \
                        f"<p>Source Code: {APP_GITHUB_LINK}</p>"
    
    APP_WINDOW = None
    APP_DOC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../documents"))