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
from exceptions import GNXError

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox, QTreeWidget, QTreeWidgetItem, QTreeView
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, Slot, QObject, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

class TreeHandler(QObject):

    gnxAlert = Signal(GNXError)

    def __init__(self, window = None, gnx = None):
        super().__init__()

        self.window = window
        self.gnx = gnx
        self.patch_name_changed_by_tree = False

        self.tree = self.window.findChild(QTreeView, "treeView")
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.rootNode = self.model.invisibleRootItem()

        self.gnxHeader = QStandardItem("GNX1")
        self.factoryHeader = QStandardItem("FACTORY")
        self.gnxHeader.appendRow(self.factoryHeader)
        self.userHeader = QStandardItem("USER")
        self.gnxHeader.appendRow(self.userHeader)

        self.libHeader = QStandardItem("LIBRARY")

        self.rootNode.appendRow(self.gnxHeader)
        self.rootNode.appendRow(self.libHeader)

        self.tree.setModel(self.model)
        self.selection = self.tree.selectionModel()
        self.selection.selectionChanged.connect(self.selectionChangedEvent)
        self.tree.expandAll()

        if self.gnx != None:
            self.setGNX(gnx)
        
    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        gnx.deviceConnectedChanged.connect(self.setConnected)
        gnx.gnxPatchNamesUpdated.connect(self.patchNamesUpdated)
        gnx.patchNameChanged.connect(self.setCurrentPatchName)

    @Slot()
    def selectionChangedEvent(self):
        for x in self.selection.selectedIndexes():
            data = x.data(Qt.UserRole)
            if data != None:
                bank = data["bank"]
                patch = data["patch"]
                print(f"Selected Bank: {bank}, Patch: {patch}")
                self.patch_name_changed_by_tree = True
                self.gnx.send_patch_change(bank, patch)
                self.patch_name_changed_by_tree = False
                pass
        pass

    @Slot()
    def setCurrentPatchXXX(self, name, bank, patch, parent = QModelIndex(), exit = False):
        if exit:
            return
        rows = self.model.rowCount(parent)
        for r in range(rows):
            index = self.model.index(r, 0, parent)
            #data = self.model.data(index)
            data = index.data(Qt.UserRole)
            if data != None:
                if data["bank"] == bank and data["patch"] == patch:
                    print(f"Received Bank: {bank}, Patch: {patch}")
                    #self.selection.blockSignals(True)
                    self.tree.setCurrentIndex(index)
                    #self.selection.blockSignals(False)
                    exit = True
                    
            if self.model.hasChildren(index):
                self.setCurrentPatch(name, bank, patch, index, exit)

    
    @Slot()
    def setCurrentPatchName(self, name, bank, patch, parent = QModelIndex(), exit = False):
        if exit:
            return
        rows = self.model.rowCount(parent)
        for r in range(rows):
            index = self.model.index(r, 0, parent)
            #data = self.model.data(index)
            data = index.data(Qt.UserRole)
            if data != None:
                if data["bank"] == bank and data["patch"] == patch:
                    print(f"Received Name: {bank}, Patch: {patch}, Name {name}")
                    index.model().setData(index, name, Qt.DisplayRole )
                    exit = True
                    
            if self.model.hasChildren(index):
                self.setCurrentPatchName(name, bank, patch, index, exit)

    @Slot()
    def setConnected(self, connected):
        pass

    @Slot()
    def patchNamesUpdated(self, bank, names):
        if self.patch_name_changed_by_tree:
            return
        if bank == 0:
            h = self.factoryHeader
        else:
            h = self.userHeader

        h.removeRows(0, h.rowCount())
        
        k = 0
        for n in names:
            w = QStandardItem(f"{(k + 1):02.0f}:{n}")
            w.setData({"bank": bank, "patch": k}, Qt.UserRole)
            h.appendRow(w)
            k += 1            

        
