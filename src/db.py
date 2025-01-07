
# db.py
#
# Copyright 2023 gary-1959
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
import sqlite3
import shutil
import settings
from exceptions import GNXError

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox, QTreeWidget, QTreeWidgetItem, QTreeView, QAbstractItemView, QMenu, QLineEdit, QMessageBox
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, Slot, QObject, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction

class gnxDB(QObject):
    
    gnxAlert = Signal(GNXError)

    def __init__(self):
        super().__init__()

        # create a database connection to a SQLite database
        self.conn = None
        try:
            rpath = os.path.realpath(__file__)
            rpath = rpath.replace("db.py", "")
            jpath = os.path.join(rpath, settings.GNXEDIT_CONFIG["library"]["path"])
            path = os.path.abspath(jpath)
            # Check whether the specified path exists or not
            pathExists = os.path.exists(path)
            if not pathExists:
                e = GNXError(icon = QMessageBox.Critical, title = "Database Error", \
                                                        text = f"No database found in path {path}", \
                                                        buttons = QMessageBox.Ok)
                e.alert(e)
                return
           
        
            self.conn = sqlite3.connect(path)
        except Exception as e:
            e = GNXError(icon = QMessageBox.Critical, title = "Database Error", \
                                                    text = f"Unable to open database on path {settings.GNXEDIT_CONFIG["library"]["path"]}", \
                                                    buttons = QMessageBox.Ok)
            e.alert(e)
            return


        


    
