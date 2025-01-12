# settings.py
#
# GNXEdit settings file
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
from appdirs import user_config_dir
import shutil
import common
from db import gnxDB
import sqlite3

def appconfig():

    common.GNXEDIT_CONFIG_PATH = user_config_dir(appname = 'GNXEdit')
    source_settings = os.path.join(os.path.dirname(__file__), "GNXEdit.json")
    source_library = os.path.join(os.path.dirname(__file__), "GNXEdit.db")

    common.GNXEDIT_CONFIG_FILE = os.path.join(common.GNXEDIT_CONFIG_PATH , "GNXEdit.json")
    common.GNXEDIT_DATABASE_FILE = os.path.join(common.GNXEDIT_CONFIG_PATH , "GNXEdit.db")

    # first time installation
    if not os.path.exists(common.GNXEDIT_CONFIG_PATH ):
        os.makedirs(common.GNXEDIT_CONFIG_PATH )
        shutil.copy2(source_settings, common.GNXEDIT_CONFIG_PATH )
        shutil.copy2(source_library, common.GNXEDIT_CONFIG_PATH )

    # check for existence of settings and database
    # settings
    if not os.path.isfile(common.GNXEDIT_CONFIG_FILE):
        shutil.copy2(source_settings, common.GNXEDIT_CONFIG_PATH )
    else:
        # check version
        current_settings = get_settings(common.GNXEDIT_CONFIG_FILE)
        if current_settings["version"] != common.APP_VERSION:
            # do settings file update here
            pass

    # database
    if not os.path.isfile(common.GNXEDIT_DATABASE_FILE):
        shutil.copy2(source_library, common.GNXEDIT_CONFIG_PATH)
    else:
        #check version
        db = gnxDB()
        if db.conn == None:
            return
    
        cur = db.conn.cursor()
        cur.execute("SELECT version FROM app")
        rc = cur.fetchone()
        if rc[0] != common.APP_VERSION:
            # do database file version update here
            pass
        db.conn.close()
    # load up settings into global variable
    common.GNXEDIT_CONFIG = get_settings()

def get_settings(file = None):
    config = None
    if file == None:
        file = common.GNXEDIT_CONFIG_FILE
    try:
        f = open(file, "r")
        config = json.loads(f.read())
        if config["midi"]["lockchannel"] != None:
            config["midi"]["channel"] = config["midi"]["lockchannel"]
        f.close()
    except Exception as e:
        print(f"Failed to load settings {e}")
        raise Exception(f"Failed to load settings.\n{e}")

    return config

def save_settings(file = None):
    if file == None:
        file = common.GNXEDIT_CONFIG_FILE
    try:
        if common.GNXEDIT_CONFIG["midi"]["lockchannel"] != None:
            common.GNXEDIT_CONFIG["midi"]["channel"] = common.GNXEDIT_CONFIG["midi"]["lockchannel"]
        f = open(file, "wt")
        f.write(json.dumps(common.GNXEDIT_CONFIG))
        f.close()
    except Exception as e:
        print(f"Settings not saved {e}")
        raise Exception(f"Failed to save settings.\n{e}")