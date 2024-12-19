# settings.py
#
# GNX Edit settings file
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

import json
import os

GNXEDIT_CONFIG = {}
GNXEDIT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "GNXEdit.json")

def get_settings():
    global GNXEDIT_CONFIG, GNXEDIT_CONFIG_FILE
    try:
        f = open(GNXEDIT_CONFIG_FILE, "r")
        GNXEDIT_CONFIG = json.loads(f.read())
        if GNXEDIT_CONFIG["midi"]["lockchannel"] != None:
            GNXEDIT_CONFIG["midi"]["channel"] = GNXEDIT_CONFIG["midi"]["lockchannel"]
        f.close()
    except Exception as e:
        print(f"Failed to load settings {e}")
        GNXEDIT_CONFIG = {}

def save_settings():
    global GNXEDIT_CONFIG, GNXEDIT_CONFIG_FILE
    try:
        if GNXEDIT_CONFIG["midi"]["lockchannel"] != None:
            GNXEDIT_CONFIG["midi"]["channel"] = GNXEDIT_CONFIG["midi"]["lockchannel"]
        f = open(GNXEDIT_CONFIG_FILE, "wt")
        f.write(json.dumps(GNXEDIT_CONFIG))
        f.close()
    except Exception as e:
        print(f"Settings not saved {e}")
