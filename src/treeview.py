# statusbar.py
#
# GNX Edit treeview handler
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

import settings
import time
from exceptions import GNXError
import sqlite3
from db import gnxDB

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox, QTreeWidget, QTreeWidgetItem, QTreeView, QAbstractItemView, QMenu, QLineEdit, QMessageBox
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, Slot, QObject, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction

# all rows with children will span columns
def findByData(parent, data):
    idx = parent.index()
    index1 = idx.siblingAtColumn(0)
    index2 = idx.siblingAtColumn(1)
    data1 = index1.data(Qt.UserRole)
    data2 = index2.data(Qt.UserRole)
    if data1 == None:
        data1 = data2

    if data1 == data:
        return parent

    if parent.hasChildren():
        for row in range(parent.rowCount()):
            result = findByData(parent.child(row, 0), data)
            if result != None:
                return result
        
        return None
    return None

def add_category_to_tree(tree, model, parent, cid, name, enabled):
    # add to tree
    cat = QStandardItem(name)
    cat.setEnabled(enabled)
    cat.setData({"role": "header", "type": "library", "category": cid}, Qt.UserRole)
    
    parent.appendRow(cat)
    ctx = model.indexFromItem(cat)
    tree.setFirstColumnSpanned(ctx.row(), model.indexFromItem(parent), True)
    tree.setExpanded(model.indexFromItem(parent), True)

class TreeHandler(QObject):

    gnxAlert = Signal(GNXError)

    def __init__(self, window = None, gnx = None):
        super().__init__()

        self.window = window
        self.gnx = gnx
        self.blockPatchChange = False
        self.current_patch_name = None
        self.current_patch_bank = None
        self.current_patch_number = None

        self.tree = self.window.findChild(QTreeView, "treeView")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.contextMenu)
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel(0, 2)
        self.rootNode = self.model.invisibleRootItem()

        self.gnxHeader = QStandardItem("GNX1")
        self.gnxHeader.setEnabled(False)
        self.gnxHeader.setData({"role": "header", "type": "gnx"}, Qt.UserRole)

        self.factoryHeader = QStandardItem("FACTORY")
        self.factoryHeader.setEnabled(False)
        self.factoryHeader.setData({"role": "header", "type": "factory"}, Qt.UserRole)
        self.gnxHeader.appendRow(self.factoryHeader)

        self.userHeader = QStandardItem("USER")
        self.userHeader.setEnabled(False)
        self.userHeader.setData({"role": "header", "type": "user"}, Qt.UserRole)
        self.gnxHeader.appendRow(self.userHeader)

        self.libHeader = QStandardItem("LIBRARY")
        self.libHeader.setEnabled(False)
        self.libHeader.setData({"role": "header", "type": "library", "category": 0}, Qt.UserRole)

        self.rootNode.appendRow(self.gnxHeader)
        self.rootNode.appendRow(self.libHeader)

        self.tree.setModel(self.model)
        self.selection = self.tree.selectionModel()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selection.selectionChanged.connect(self.selectionChangedEvent)

        self.tree.model().dataChanged.connect(self.dataChanged)

        self.setHeaderSpanned(self.tree.model().invisibleRootItem())

        # add library data

        db = gnxDB()
        if db.conn == None:
            return
        
        try:
            db.conn.row_factory = sqlite3.Row
            cur = db.conn.cursor()
            cur.execute("SELECT * FROM categories ORDER by parent ASC")
            rc = cur.fetchall()
            crows = [dict(row) for row in rc]

            for c in crows:
                data = {"role": "header", "type": "library", "category": c["parent"]} # look for parent
                pcat = findByData(self.libHeader, data)
                add_category_to_tree(self.tree, self.model, pcat, c["id"], c["name"], False)
            pass

        except Exception as e:
            e = GNXError(icon = QMessageBox.Critical, title = "Add Category Error", \
                                                    text = f"Unable to add category to tree {e}", \
                                                    buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)  

        if self.gnx != None:
            self.setGNX(gnx)
    
    def contextMenu(self, point):
        index = self.tree.indexAt(point)
        if index.isValid():
            d1 = index.data(Qt.UserRole)
            if d1 != None and d1["role"] == "header" and d1["type"] == "library":
                contextMenu = QMenu(self.tree)
                actions = [{"text": "Add Category", "connect": self.addCategory}]
                for a in actions:
                    action = QAction(a["text"])
                    action.triggered.connect(a["connect"])
                    action.setData(d1)
                    contextMenu.addAction(action)

                contextMenu.exec(self.tree.viewport().mapToGlobal(point))

    @Slot()
    def addCategory(self):
        sender = self.sender()
        data = sender.data()

        ui_file_name = "src/ui/addcategorydialog.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            e = GNXError(icon = QMessageBox.Critical, title = "Add Category Error", \
                                        text = f"Cannot open {ui_file_name}: {ui_file.errorString()}", \
                                        buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e) 
            return

        loader = QUiLoader()
        self.add_category_dialog = loader.load(ui_file)

        ui_file.close()
        inputName = self.add_category_dialog.findChild(QLineEdit, "inputName")
        inputName.setText("New Category")

        setattr(self.add_category_dialog, "gnxdata", data)
        self.add_category_dialog.accepted.connect(self.add_category_dialog_accepted)
        self.add_category_dialog.rejected.connect(self.add_category_dialog_rejected)
        self.add_category_dialog.setParent(self.window, Qt.Dialog)
        self.add_category_dialog.show()

    def add_category_dialog_accepted(self):
        data = getattr(self.add_category_dialog, "gnxdata")
        inputName = self.add_category_dialog.findChild(QLineEdit, "inputName")
        name = inputName.text()

        name = name.strip()
        if name != None and name != "":
            db = gnxDB()
            if db.conn == None:
                return
            
            try:
                cur = db.conn.cursor()
                cur.execute("INSERT INTO categories (parent, name) VALUES (?, ?)", [data["category"], name])
                db.conn.commit()

                # add to tree
                pcat = findByData(self.libHeader, data)
                add_category_to_tree(self.tree, self.model, pcat, cur.lastrowid, name, False)

            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Add Category Error", \
                                                        text = f"Unable to add category to database {e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)                

        else:
            e = GNXError(icon = QMessageBox.Critical, title = "Add Category Error", \
                                                    text = f"Empty category name not permitted", \
                                                    buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)

    def add_category_dialog_rejected(self):
        pass

    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        self.gnx.deviceConnectedChanged.connect(self.setConnected)
        self.gnx.gnxPatchNamesUpdated.connect(self.patchNamesUpdated)
        self.gnx.patchNameChanged.connect(self.setCurrentPatch)
        #self.gnx.midiPatchChange.connect(self.midiPatchChange)             # patch number may be mapped - do not use

    @Slot()
    def dataChanged(self, topleft, bottomright, roles):
        if Qt.EditRole in roles:
            text = topleft.data(Qt.EditRole)
            if len(text) > 6:
                text = text[0:6]
            data = topleft.data(Qt.UserRole)
            if data["role"] == "patch" and data["type"] == "user":
                bank = data["bank"]
                patch = data["patch"]
            

            #model = topleft.model()
            #item = model.itemFromIndex(topleft)
            #item.setData(text, Qt.DisplayRole)

            self.gnx.save_patch(text, bank, patch, bank, patch)

    @Slot()
    def midiPatchChange(self, parameter):
        bank = int(parameter / 48)
        patch = parameter % 48
        self.setPatchInTree(None, bank, patch, QModelIndex())

    @Slot()
    def selectionChangedEvent(self):
        for x in self.selection.selectedIndexes():
            data = x.data(Qt.UserRole)
            if data["role"] == "patch":
                bank = data["bank"]
                patch = data["patch"]
                if not self.blockPatchChange:
                    self.gnx.send_patch_change(bank, patch)
                pass
        pass

    @Slot()
    def setCurrentPatch(self, name, bank, patch):
        self.setPatchInTree(name, bank, patch, parent = QModelIndex())

    def setPatchInTree(self, name, bank, patch, parent):
        # do not start or exit through recursion if set
        if self.current_patch_name == name and self.current_patch_bank == bank and self.current_patch_number == patch:
            return

        rows = self.model.rowCount(parent)
        for r in range(rows):
            index1 = self.model.index(r, 0, parent)
            index2 = self.model.index(r, 1, parent)
            data1 = index1.data(Qt.UserRole)
            data2 = index2.data(Qt.UserRole)
            if data1 == None:
                data1 = data2 
            if data1["role"] == "patch":
                if data1["bank"] == bank and data1["patch"] == patch:

                    if name != None:
                        index2.model().setData(index2, name, Qt.DisplayRole )
                        self.current_patch_name = name
                    else:
                        name = self.current_patch_name  #to exit recurion
                    self.current_patch_bank = bank
                    self.current_patch_number = patch
                    #self.tree.selectionModel().blockSignals(True)   - DO NOT USE prevents tree update
                    self.blockPatchChange = True
                    self.tree.selectionModel().clearSelection()
                    self.tree.selectionModel().clearCurrentIndex()
                    self.tree.selectionModel().select(index2, QItemSelectionModel.ClearAndSelect)
                    self.blockPatchChange = False
                    #self.tree.selectionModel().blockSignals(False)
                    break
            # recursion
            if self.model.hasChildren(index1):
                self.setPatchInTree(name, bank, patch, index1)

    @Slot()
    def setConnected(self, connected):
        if not connected:
            self.current_patch_bank = None
            self.current_patch_number = None
            self.current_patch_name = None
        pass

    # populate tree
    @Slot()
    def patchNamesUpdated(self, bank, names):

        if bank == 0:
            h = self.factoryHeader
        else:
            h = self.userHeader

        h.removeRows(0, h.rowCount())
        
        k = 0
        for n in names:
            w1 = QStandardItem(f"{(k + 1):02.0f}:")
            w2 = QStandardItem(n)
            w1.setEnabled(False)
            if w2 != None:
                w2.setEditable(bank == 1)   # only user bank is editable

            w2.setData({"role": "patch", "type": "factory" if bank == 0 else "user", "bank": bank, "patch": k}, Qt.UserRole)
            h.appendRow([w1, w2])
            k += 1

        self.setHeaderSpanned(self.tree.model().invisibleRootItem())

    # all rows with children will span comlumns
    def setHeaderSpanned(self, parent):
        idx = parent.index()
        for row in range(parent.rowCount()):

            index1 = self.model.index(row, 0, idx)
            index2 = self.model.index(row, 1, idx)
            data1 = index1.data(Qt.UserRole)
            data2 = index2.data(Qt.UserRole)
            if data1 == None:
                data1 = data2 

            if parent.child(row, 0).hasChildren() or data1["role"] == "header":
                self.tree.setFirstColumnSpanned(row, idx, True)

            if parent.child(row, 0).hasChildren():
                self.setHeaderSpanned(parent.child(row, 0))


    