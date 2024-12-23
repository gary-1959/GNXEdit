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

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox, QTreeWidget, QTreeWidgetItem, QTreeView, QAbstractItemView
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, Slot, QObject, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

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
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel(0, 2)
        self.rootNode = self.model.invisibleRootItem()

        self.gnxHeader = QStandardItem("GNX1")
        self.gnxHeader.setEnabled(False)
        self.gnxHeader.setData("header", Qt.UserRole)

        self.factoryHeader = QStandardItem("FACTORY")
        self.factoryHeader.setEnabled(False)
        self.factoryHeader.setData("header", Qt.UserRole)
        self.gnxHeader.appendRow(self.factoryHeader)

        self.userHeader = QStandardItem("USER")
        self.userHeader.setEnabled(False)
        self.userHeader.setData("header", Qt.UserRole)
        self.gnxHeader.appendRow(self.userHeader)

        self.libHeader = QStandardItem("LIBRARY")
        self.libHeader.setEnabled(False)
        self.libHeader.setData("header", Qt.UserRole)

        self.rootNode.appendRow(self.gnxHeader)
        self.rootNode.appendRow(self.libHeader)

        self.tree.setModel(self.model)
        self.selection = self.tree.selectionModel()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selection.selectionChanged.connect(self.selectionChangedEvent)

        self.tree.model().dataChanged.connect(self.dataChanged)

        self.setHeaderSpanned(self.tree.model().invisibleRootItem())

        if self.gnx != None:
            self.setGNX(gnx)
        
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
            bank = data["bank"]
            patch = data["patch"]
            

            #model = topleft.model()
            #item = model.itemFromIndex(topleft)
            #item.setData(text, Qt.DisplayRole)

            self.gnx.send_patch_name(text, bank, patch, bank, patch)

    @Slot()
    def midiPatchChange(self, parameter):
        bank = int(parameter / 48)
        patch = parameter % 48
        print(f"Tree MIDI Patch Change: Bank: {bank}, Patch: {patch}")
        self.setPatchInTree(None, bank, patch, QModelIndex())

    @Slot()
    def selectionChangedEvent(self):
        for x in self.selection.selectedIndexes():
            data = x.data(Qt.UserRole)
            if data != None and data != "header":
                bank = data["bank"]
                patch = data["patch"]
                blocked = "BLOCKED" if self.blockPatchChange else ""
                print(f"Tree Selection Changed Bank: {bank}, Patch: {patch} {blocked}")
                if not self.blockPatchChange:
                    self.gnx.send_patch_change(bank, patch)
                pass
        pass

    @Slot()
    def setCurrentPatch(self, name, bank, patch):
        print(f"Received from GNX Bank: {bank}, Patch: {patch}, Name {name}")
        self.setPatchInTree(name, bank, patch, parent = QModelIndex())

    def setPatchInTree(self, name, bank, patch, parent):
        # do not start or exit through recursion if set
        if self.current_patch_name == name and self.current_patch_bank == bank and self.current_patch_number == patch:
            return

        rows = self.model.rowCount(parent)
        for r in range(rows):
            index1 = self.model.index(r, 0, parent)
            index2 = self.model.index(r, 1, parent)
            data = index2.data(Qt.UserRole)
            if data != None and data != "header":
                if data["bank"] == bank and data["patch"] == patch:

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

            w2.setData({"bank": bank, "patch": k}, Qt.UserRole)
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

            #print(idx.data(Qt.DisplayRole), data1, data2)

            if parent.child(row, 0).hasChildren() or data1 == "header":
                self.tree.setFirstColumnSpanned(row, idx, True)

            if parent.child(row, 0).hasChildren():
                self.setHeaderSpanned(parent.child(row, 0))