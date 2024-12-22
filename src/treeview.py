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

        self.factoryHeader = QStandardItem("FACTORY")
        self.factoryHeader.setEnabled(False)
        self.gnxHeader.appendRow(self.factoryHeader)

        self.userHeader = QStandardItem("USER")
        self.userHeader.setEnabled(False)
        self.gnxHeader.appendRow(self.userHeader)

        self.libHeader = QStandardItem("LIBRARY")
        self.libHeader.setEnabled(False)

        self.rootNode.appendRow(self.gnxHeader)
        self.rootNode.appendRow(self.libHeader)

        self.tree.setModel(self.model)
        self.selection = self.tree.selectionModel()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selection.selectionChanged.connect(self.selectionChangedEvent)

        self.tree.setFirstColumnSpanned(self.factoryHeader.index().row(), QModelIndex(), True)

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
    def midiPatchChange(self, parameter):
        bank = int(parameter / 48)
        patch = parameter % 48
        print(f"Tree MIDI Patch Change: Bank: {bank}, Patch: {patch}")
        self.setPatchInTree(None, bank, patch, QModelIndex())

    @Slot()
    def selectionChangedEvent(self):
        for x in self.selection.selectedIndexes():
            data = x.data(Qt.UserRole)
            if data != None:
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
            index = self.model.index(r, 0, parent)
            #data = self.model.data(index)
            data = index.data(Qt.UserRole)
            if data != None:
                if data["bank"] == bank and data["patch"] == patch:

                    if name != None:
                        index.model().setData(index, f"{(patch + 1):02.0f}:{name}", Qt.DisplayRole )
                        self.current_patch_name = name
                    else:
                        name = self.current_patch_name  #to exit recurion
                    self.current_patch_bank = bank
                    self.current_patch_number = patch
                    #self.tree.selectionModel().blockSignals(True)
                    self.blockPatchChange = True
                    self.tree.selectionModel().clearSelection()
                    self.tree.selectionModel().clearCurrentIndex()
                    self.tree.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
                    self.blockPatchChange = False
                    #self.tree.selectionModel().blockSignals(False)
                    break
            # recursion
            if self.model.hasChildren(index):
                self.setPatchInTree(name, bank, patch, index)

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
            w1.setEnabled(False)
            w2 = QStandardItem(n)
            w2.setData({"bank": bank, "patch": k}, Qt.UserRole)
            h.appendRow([w1, w2])
            k += 1            

        
