# statusbar.py
#
# GNXEdit treeview handler
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
import types
import re
from exceptions import GNXError
import sqlite3
from db import gnxDB

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QSpinBox, QTreeWidget, QPlainTextEdit, QTreeView, \
            QAbstractItemView, QMenu, QLineEdit, QMessageBox, QStyleOptionViewItem, QLabel, QWidgetAction, QPushButton, QGroupBox, QTextEdit
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, Slot, QObject, QModelIndex, QItemSelectionModel, QRegularExpression, QTimer, \
            QPropertyAnimation, QRect, QSequentialAnimationGroup
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QPainter, QRegularExpressionValidator, QValidator, QColor

class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        # Custom painting of items
        #painter.save()
        #value = index.data(Qt.DisplayRole)
        #if value:
        #    painter.setPen(Qt.red)
        #    painter.drawText(option.rect, Qt.AlignLeft, f"Custom: {value}")
        #painter.restore()
        super().paint(painter, option, index)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        # Custom editor widget
        self.editor = QLineEdit(parent)
        # Set data from model to editor
        data = index.data(Qt.UserRole)
        if data["role"] == "patch":
            rx = QRegularExpression(r".{3, 6}+")
            validator = QRegularExpressionValidator(rx)
            self.editor.setValidator(validator)
            self.editor.setMaxLength(6)
            self.editor.setPlaceholderText(f"2-6 characters")
        else:
            rx = QRegularExpression(r".{3, 32}")
            validator = QRegularExpressionValidator(rx)
            self.editor.setValidator(validator)
            self.editor.setMaxLength(32)
            self.editor.setPlaceholderText(f"2-32 characters")

        self.editor.textChanged.connect(self.textChanged)

        return self.editor
    
    def textChanged(self):
        if self.editor.hasAcceptableInput():
            self.editor.setStyleSheet("background-color: white")
        else:
            self.editor.setStyleSheet("background-color: palegoldenrod")
        
    def setEditorData(self, editor: QWidget, index: QModelIndex):
        
        value = index.data(Qt.EditRole) or index.data(Qt.DisplayRole)
        if isinstance(editor, QLineEdit):
            editor.setText(value)

    def setModelData(self, editor: QWidget, model, index: QModelIndex):
        # Save data from editor back to model
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.EditRole)

# all rows with children will span columns
def findByData(parent, data):
    idx = parent.index()
    index1 = idx.siblingAtColumn(0)
    data1 = index1.data(Qt.UserRole)

    # compare only supplied parts of data
    # it's up to the calling routine to make sure this is suitably specific
    found = True
    for k, d in data.items():
        if k in data1:
            if data1[k] == d:
                continue
            else:
                found = False
                break
        else:
            found = False
            break

    if found:
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
    if parent != None:     
        cat = QStandardItem(name)
        cat.setForeground(Qt.magenta)
        cat.setEnabled(enabled)
        data = {"role": "header", "type": "library", "category": cid, "name": name}
        cat.setData(data, Qt.UserRole)
        
        parent.appendRow(cat)
        ctx = model.indexFromItem(cat)
        tree.setItemDelegateForRow(ctx.row(), CustomDelegate(tree))
        tree.setFirstColumnSpanned(ctx.row(), model.indexFromItem(parent), True)
        tree.setExpanded(model.indexFromItem(parent), True)
        model.layoutChanged
        return cat
    else:
        return None

def add_patch_to_tree(tree = None, model = None, parent = None, type = "", bank = None, patch_num = None,
                               patch_id = None, name = "", description = "", tags = "" ):
    if type == "library":
        w1 = QStandardItem(name)
        w1.setForeground(Qt.green)
        w1.setEnabled(True)
        w1.setEditable(True)   # library patch name is editable
        data = {"role": "patch", "type": "library", "bank": None, "patch": patch_id, "name": name,
                    "description": description, "tags": tags}
        w1.setData(data, Qt.UserRole)
        parent.appendRow([w1])
        ctx = model.indexFromItem(w1)
        tree.setItemDelegateForRow(ctx.row(), CustomDelegate(tree))
        tree.setFirstColumnSpanned(ctx.row(), model.indexFromItem(parent), True)
        tree.setExpanded(model.indexFromItem(parent), True)
        w2 = None
        
    else:
        w1 = QStandardItem(f"{(patch_num + 1):02.0f}:")
        w2 = QStandardItem(name)
        w1.setEnabled(True)
        w1.setEditable(False)
        if w2 != None:
            w2.setEditable(bank == 1)   # only user bank is editable

        color = Qt.red if bank == 0 else Qt.green
        w1.setForeground(color)
        w2.setForeground(color)

        data = {"role": "patch", "type": "factory" if bank == 0 else "user", "bank": bank, "patch": patch_num, "name": name}
        w1.setData(data, Qt.UserRole)
        w2.setData(data, Qt.UserRole)
        parent.appendRow([w1, w2])
        ctx = model.indexFromItem(w2)
        tree.setItemDelegateForRow(ctx.row(), CustomDelegate(tree))

    model.layoutChanged
    return w1, w2

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
        self.clipBoard = None

        self.tree = self.window.findChild(QTreeView, "treeView")
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.contextMenu)
        self.tree.setHeaderHidden(True)
        
        self.model = QStandardItemModel(0, 2)
        self.rootNode = self.model.invisibleRootItem()

        self.gnxHeader = QStandardItem("GNX1")
        self.gnxHeader.setEnabled(False)
        self.rootNode.appendRow(self.gnxHeader)     # important to append before setting data so that dat appears in model
        self.gnxHeader.setData({"role": "header", "type": "gnx"}, Qt.UserRole)

        self.factoryHeader = QStandardItem("FACTORY")
        self.factoryHeader.setEnabled(False)
        self.gnxHeader.appendRow(self.factoryHeader)
        self.factoryHeader.setData({"role": "header", "type": "factory"}, Qt.UserRole)

        self.userHeader = QStandardItem("USER")
        self.userHeader.setEnabled(False)
        self.gnxHeader.appendRow(self.userHeader)
        self.userHeader.setData({"role": "header", "type": "user"}, Qt.UserRole)

        self.libHeader = QStandardItem("LIBRARY")
        self.libHeader.setEnabled(True)
        self.libHeader.setEditable(False)
        self.rootNode.appendRow(self.libHeader)
        self.libHeader.setData({"role": "header", "type": "library", "category": 0}, Qt.UserRole)

        self.tree.setModel(self.model)
        self.selection = self.tree.selectionModel()
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selection.selectionChanged.connect(self.selectionChangedEvent)

        self.tree.model().dataChanged.connect(self.dataChanged)
        self.tree.model().itemChanged.connect(self.itemChanged)

        self.setHeaderSpanned(self.tree.model().invisibleRootItem())

        # patch details box

        self.patchDetailsGroupBox = self.window.findChild(QGroupBox, "patchDetailsGroupBox")
        self.patchDescription = self.window.findChild(QPlainTextEdit, "patchDescription")
        self.patchTags = self.window.findChild(QPlainTextEdit, "patchTags")
        self.patchUpdateButton = self.window.findChild(QPushButton, "patchDescriptionUpdateButton")
        self.patchUpdateButton.clicked.connect(self.patchUpdateButtonClicked)
        
        # animation for show/hide patch details box
        self.patchDetailsAnimationShow = QPropertyAnimation(self.patchDetailsGroupBox, b"maximumHeight")
        self.patchDetailsAnimationShow.setDuration(500)
        rect = self.patchDetailsGroupBox.geometry()
        self.patchDetailsAnimationShow.setStartValue(0)
        self.patchDetailsAnimationShow.setEndValue(rect.height())
        
        self.patchDetailsAnimationHide = QPropertyAnimation(self.patchDetailsGroupBox, b"maximumHeight")
        self.patchDetailsAnimationHide.setDuration(500)
        self.patchDetailsAnimationHide.setStartValue(rect.height())
        self.patchDetailsAnimationHide.setEndValue(0)

        self.patchDetailsGroupBox.setMaximumHeight(0)

        # search results box

        self.searchResults = self.window.findChild(QTextEdit, "searchResults")
        self.searchResults.setOwner(self)
        self.searchResultsGroupBox = self.window.findChild(QGroupBox, "searchResultsGroupBox")
        self.searchResultsHideButton = self.window.findChild(QPushButton, "searchResultsHideButton")

        # animation for show/hide search results box
        self.searchResultsAnimationShow = QPropertyAnimation(self.searchResultsGroupBox, b"maximumHeight")
        self.searchResultsAnimationShow.setDuration(500)
        rect = self.searchResultsGroupBox.geometry()
        self.searchResultsAnimationShow.setStartValue(0)
        self.searchResultsAnimationShow.setEndValue(rect.height())
        
        self.searchResultsAnimationHide = QPropertyAnimation(self.searchResultsGroupBox, b"maximumHeight")
        self.searchResultsAnimationHide.setDuration(500)
        self.searchResultsAnimationHide.setStartValue(rect.height())
        self.searchResultsAnimationHide.setEndValue(0)

        self.searchResultsHideButton.clicked.connect(self.searchResultsAnimationHide.start)
        self.searchResultsGroupBox.setMaximumHeight(0)

        # search input
        self.patchSearchText = self.window.findChild(QLineEdit, "patchSearchText")
        self.patchSearchButton = self.window.findChild(QPushButton, "patchSearchButton")
        self.patchSearchButton.clicked.connect(self.searchButtonClicked)

        # add library data
        
        try:
            db = gnxDB()
            if db.conn == None:
                return
            db.conn.row_factory = sqlite3.Row
            cur = db.conn.cursor()
            cur.execute("SELECT c.parent AS cat_parent, c.id as cat_id, c.name as cat_name, \
		                    p.id AS patch_id, p.name AS patch_name, p.description AS patch_description, p.tags AS patch_tags, \
                            c2.id AS parent_id \
	                        FROM categories AS c \
	                        LEFT JOIN patches AS p ON p.category = c.id \
                            LEFT JOIN categories AS c2 on c.parent = c2.id \
                            WHERE cat_parent IS NOT NULL \
                            ORDER by cat_parent, cat_id, patch_name ASC")
            rc = cur.fetchall()
            crows = [dict(row) for row in rc]

            last_cat = None
            cat = None

            for c in crows:
                if last_cat != c["cat_id"]:
                    data = {"role": "header", "type": "library", "category": c["cat_parent"]} # look for parent
                    pcat = findByData(self.libHeader, data)
                    if pcat != None:
                        cat = add_category_to_tree(self.tree, self.model, pcat, c["cat_id"], c["cat_name"], True)
                        last_cat = c["cat_id"]

                if c["patch_id"] != None:
                    add_patch_to_tree(tree = self.tree, model = self.model, parent = cat, type = "library", 
                        patch_id = c["patch_id"], name = c["patch_name"], description = c["patch_description"], tags = c["patch_tags"])

            db.conn.close()

        except Exception as e:
            e = GNXError(icon = QMessageBox.Critical, title = "Add Category Error", \
                                                    text = f"Unable to add category to tree\n{e}", \
                                                    buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)  

        if self.gnx != None:
            self.setGNX(gnx)
    
    def contextMenu(self, point):
        index = self.tree.indexAt(point)
        actions = None
        title = None
        if index.isValid():
            d1 = index.data(Qt.UserRole)
            if d1 != None and d1["role"] == "header" and d1["type"] == "library":
                title = "CATEGORY"
                if d1["category"] == 0:     # library root

                    actions = [{"text": "Add Category", "connect": self.addCategory},
                            {"text": "---", "connect": None},
                            {"text": "Copy", "connect": self.copyBranch},
                            {"text": "Paste", "connect": self.pasteBranch}
                    ]

                else:
                    actions = [{"text": "Add Category", "connect": self.addCategory},
                            {"text": "Edit", "connect": self.editCategory},
                            {"text": "---", "connect": None},
                            {"text": "Cut", "connect": self.cutBranch},
                            {"text": "Copy", "connect": self.copyBranch},
                            {"text": "Paste", "connect": self.pasteBranch},
                            {"text": "---", "connect": None},
                            {"text": "Delete", "connect": self.deleteCategory}
                    ]

            elif d1 != None and d1["role"] == "patch" and d1["type"] == "library":
                title = "PATCH"
                actions = [{"text": "Edit", "connect": self.editPatch},
                           {"text": "Send Patch to GNX", "connect": self.sendPatch},
                           {"text": "---", "connect": None},
                           {"text": "Cut", "connect": self.cutBranch},
                           {"text": "Copy", "connect": self.copyBranch},
                           {"text": "---", "connect": None},
                           {"text": "Delete", "connect": self.deletePatch}
                ]

            if actions != None:
                cm = QMenu(self.tree)
                cm.setProperty("cssClass", "context-menu")
                if title != None:
                    label = QLabel(title)
                    label.setProperty("cssClass", "context-menu-title")
                    widget = QWidgetAction(cm)
                    widget.setDefaultWidget(label)
                    cm.addAction(widget)

                    x = cm.actions()
                    cm.addSeparator()
                for a in actions:
                    if a["text"] == "---":
                        cm.addSeparator()
                        pass
                    else:
                        action = QAction(a["text"])
                        action.triggered.connect(a["connect"])
                        action.setData(d1)
                        cm.addAction(action)
                        x = cm.actions()

                cm.exec(self.tree.viewport().mapToGlobal(point))

    @Slot()
    def noAction(self):
        pass

    @Slot()
    def sendPatch(self):
        sender = self.sender()
        data = sender.data()
        self.gnx.send_to_device(data["patch"])

    @Slot()
    def editPatch(self):
        sender = self.sender()
        data = sender.data()

        def accepted():

            name = inputName.text().upper()
            description = inputDescription.toPlainText().upper()
            tags = inputTags.toPlainText().upper()

            try:
                db = gnxDB()
                if db.conn == None:
                    return

                cur = db.conn.cursor()
                cur.execute("UPDATE patches SET name = ?, description = ?, tags = ? WHERE id = ?", [name, description, tags, data["patch"]])
                db.conn.commit()
                db.conn.close()

                patch = findByData(self.libHeader, data)
                data["name"] = name
                data["description"] = description
                data["tags"] = tags
                patch.setData(data, Qt.UserRole)
                patch.setData(name, Qt.DisplayRole)

                self.setDescriptionAndTags(data)

            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Edit Patch Error", \
                                                        text = f"Unable to update patch in database\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)     
            

        def rejected():
            pass

        ui_file_name = "src/ui/editlibrarypatchdialog.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            e = GNXError(icon = QMessageBox.Alert, title = "Edit Patch Error", \
                        text = f"Cannot open {ui_file_name}: {ui_file.errorString()}", buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)
            return

        loader = QUiLoader()
        dialog = loader.load(ui_file)

        ui_file.close()
        inputName = dialog.findChild(QLineEdit, "inputName")
        inputDescription = dialog.findChild(QPlainTextEdit, "inputDescription")
        inputTags = dialog.findChild(QPlainTextEdit, "inputTags")

        inputName.setText(data["name"])
        inputDescription.setPlainText(data["description"])
        inputTags.setPlainText(data["tags"])

        dialog.accepted.connect(accepted)
        dialog.rejected.connect(rejected)
        dialog.setParent(self.window, Qt.Dialog)
        dialog.show()

    @Slot()
    def deletePatch(self):
        sender = self.sender()
        data = sender.data()

        result = QMessageBox.question(self.window, "Delete Patch", 
                                      "This will permanently delete this patch.\nAre you sure you want to continue?", 
                                      QMessageBox.Cancel | QMessageBox.Yes, QMessageBox.Cancel)
        if result == QMessageBox.Yes:
            try:
                db = gnxDB()
                if db.conn == None:
                    return
            
                cur = db.conn.cursor()

                cur.execute("DELETE FROM patches WHERE id = ?", [data["patch"]])
                db.conn.commit()

                # remove from tree
                patch = findByData(self.libHeader, data)
                p = patch.index()
                self.model.removeRow(patch.index().row(), patch.index().parent())

            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Delete Patch Error", \
                                                        text = f"Unable to delete patch from database.\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)     
            db.conn.close() 
            self.model.layoutChanged

    @Slot()
    def addCategory(self):
        sender = self.sender()

        self.categoryDialog(sender = sender, edit = False)

    @Slot()
    def editCategory(self):
        sender = self.sender()
        self.categoryDialog(sender = sender, edit = True)

    def categoryDialog(self, sender = None, edit = False):
        def accepted():

            name = inputName.text().upper()
            name = name.strip()
            if name != None and name != "":
                try:
                    db = gnxDB()
                    if db.conn == None:
                        return
                    cur = db.conn.cursor()

                    if edit:
                        cur.execute("UPDATE categories SET name = ? WHERE id = ?", [name, data["category"]])
                        db.conn.commit()

                        # update tree
                        pcat = findByData(self.libHeader, data)
                        data["name"] = name
                        pcat.setData(data, Qt.UserRole)
                        pcat.setData(name, Qt.DisplayRole)

                    else:
                        cur.execute("INSERT INTO categories (parent, name) VALUES (?, ?)", [data["category"], name])
                        db.conn.commit()

                        # add to tree
                        pcat = findByData(self.libHeader, data)
                        add_category_to_tree(self.tree, self.model, pcat, cur.lastrowid, name, True)

                except Exception as ex:
                    dtext = ["Edit Category Error", f"Unable to update category in database\n{ex}"] \
                                if edit else ["Add Category Error", f"Unable to add category to database\n{ex}"]
                    e = GNXError(icon = QMessageBox.Critical, title = dtext[0], \
                                                            text = dtext[1], \
                                                            buttons = QMessageBox.Ok)
                    self.gnxAlert.emit(e)     
                db.conn.close()           

            else:
                e = GNXError(icon = QMessageBox.Critical, title = f"{title} Category Error", \
                                                        text = f"Empty category name not permitted", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)

        def rejected():
            pass

        data = sender.data()

        title = "Edit" if edit else "Add"

        ui_file_name = "src/ui/addcategorydialog.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            e = GNXError(icon = QMessageBox.Critical, title = f"{title} Category Error", \
                                        text = f"Cannot open {ui_file_name}: {ui_file.errorString()}", \
                                        buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e) 
            return

        loader = QUiLoader()
        dialog = loader.load(ui_file)

        ui_file.close()
        inputName = dialog.findChild(QLineEdit, "inputName")
        if edit:
            inputName.setText(data["name"])
        else:
            inputName.setText("NEW CATEGORY")

        setattr(dialog, "gnxdata", data)
        dialog.accepted.connect(accepted)
        dialog.rejected.connect(rejected)
        dialog.setParent(self.window, Qt.Dialog)
        dialog.setWindowTitle(f"{title} Category")
        dialog.show()

    @Slot()
    def cutBranch(self):
        self.cutCopyBranch(self.sender(), "cut")

    @Slot()
    def copyBranch(self):
        self.cutCopyBranch(self.sender(), "copy")

    def cutCopyBranch(self, sender, mode):
        data = sender.data()
        parent = findByData(self.libHeader, data)
        self.clipBoard = self.addBranchToClipboard(parent, mode, [])
        pass

        # build category tree on clipboard

    def addBranchToClipboard(self, parent, mode, branch):
        idx = parent.index()
        index1 = idx.siblingAtColumn(0)
        data1 = index1.data(Qt.UserRole)

        if data1["role"] == "patch":
            try:
                db = gnxDB()
                if db.conn == None:
                    return
                db.conn.row_factory = sqlite3.Row
                cur = db.conn.cursor()
                cur.execute("SELECT * FROM patches WHERE id = ?", [data1["patch"]])
                rc = cur.fetchall()
                row = [dict(row) for row in rc]
                branch.append({"type": "patch", "mode": mode, "data": row[0]})
                db.conn.close()
            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Clipboard Error", \
                                                        text = f"Unable to retrieve patch data from database\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)
                return
        elif data1["role"] == "header":
            try:
                db = gnxDB()
                if db.conn == None:
                    return
                db.conn.row_factory = sqlite3.Row
                cur = db.conn.cursor()
                cur.execute("SELECT * FROM categories WHERE id = ?", [data1["category"]])
                rc = cur.fetchall()
                row = [dict(row) for row in rc]
                if len(row) > 0:
                    branch.append({"type": "category", "mode": mode, "data": row[0]})
                db.conn.close()
            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Clipboard Error", \
                                                        text = f"Unable to retrieve patch data from database\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)
                return

        if parent.hasChildren():
            for row in range(parent.rowCount()):
                branch = self.addBranchToClipboard(parent.child(row, 0), mode, branch)
        return branch

    @Slot()
    def pasteBranch(self):
        sender = self.sender()  # target
        data = sender.data()

        # as categories are added, parent links need to be remapped.
        # create source/target stack starting with paste target which is unchanged

        parents = {}
        parents[data["category"]] = data["category"]

        if self.clipBoard[0]["mode"] == "cut":

            # check that clipboard is not being pasted into a category contained in clipboard
            # otherwise deleting source deletes everything
            for c in self.clipBoard:
                if c["type"] == "category":
                    if c["data"]["id"] == data["category"]:
                        e = GNXError(icon = QMessageBox.Critical, title = "Cut and Paste Category Error", \
                                                                text = f"Operation not permitted here\nUnable to delete source category because it would delete the newly pasted items.", \
                                                                buttons = QMessageBox.Ok)
                        self.gnxAlert.emit(e)
                        return
                pass

        for clip in self.clipBoard:
            if clip["type"] == "patch":
                clipdata = clip["data"]
                try:
                    db = gnxDB()
                    if db.conn == None:
                        return

                    # remap parent
                    if clipdata["category"] not in parents:
                        newparent = data["category"]
                    else:
                        newparent = parents[clipdata["category"]]
                    
                    cur = db.conn.cursor()
                    cur.execute("INSERT INTO patches (category, name, description, tags, C24, C26, C28, C3C06, C3D07, C3C08, C3D09) \
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                [newparent, clipdata["name"], clipdata["description"], clipdata["tags"],
                                clipdata["C24"], clipdata["C26"], clipdata["C28"], clipdata["C3C06"], clipdata["C3D07"], 
                                clipdata["C3C08"], clipdata["C3D09"]])
                    db.conn.commit()

                    # add to tree
                    pcat = findByData(self.libHeader, {"role": "header", "type": "library", "category": newparent})
                    id = cur.lastrowid
                    add_patch_to_tree(tree = self.tree, model = self.model, parent = pcat, type="library", patch_id = id,
                                    name = clipdata["name"], description = clipdata["description"], tags = clipdata["tags"])
                    
                    if clip["mode"] == "cut":
                        cur.execute("DELETE FROM patches WHERE id = ?", [clipdata["id"]])
                        db.conn.commit()

                        # remove from tree
                        dpatch = {"role": "patch", "type": "library", "bank": None, "patch": clipdata["id"]}
                        patch = findByData(self.libHeader, dpatch)
                        if patch != None:   # already deleted, multiple pastes
                            self.model.removeRow(patch.index().row(), patch.index().parent())        
            
                except Exception as e:
                    e = GNXError(icon = QMessageBox.Critical, title = "Paste Patch Error", \
                                                            text = f"Unable to add patch to database\n{e}", \
                                                            buttons = QMessageBox.Ok)
                    self.gnxAlert.emit(e)     
                db.conn.close()

            elif clip["type"] == "category":
                clipdata = clip["data"]

                try:
                    db = gnxDB()
                    if db.conn == None:
                        return
                    
                    # remap parent
                    if clipdata["parent"] not in parents:
                        newparent = data["category"]
                    else:
                        newparent = parents[clipdata["parent"]]
                
                    cur = db.conn.cursor()
                    cur.execute("INSERT INTO categories (parent, name) VALUES (?, ?)", [newparent, clipdata["name"]])
                    db.conn.commit()

                    # add to tree
                    pcat = findByData(self.libHeader, {"role": "header", "type": "library", "category": newparent})
                    id = cur.lastrowid
                    parents[clipdata["id"]] = id  # add remapped parent
                    add_category_to_tree(tree = self.tree, model = self.model, parent = pcat, cid = id, name = clipdata["name"], enabled = True)
                    
                    if clip["mode"] == "cut":

                        cur.execute("DELETE FROM categories WHERE id = ?", [clipdata["id"]])
                        db.conn.commit()

                        # remove from tree
                        dpatch = {"role": "header", "type": "library", "category": clipdata["id"]}
                        patch = findByData(self.libHeader, dpatch)
                        if patch != None:   # already deleted, multiple pastes
                            self.model.removeRow(patch.index().row(), patch.index().parent())        
            
                except Exception as e:
                    e = GNXError(icon = QMessageBox.Critical, title = "Paste Category Error", \
                                                            text = f"Unable to add category to database\n{e}", \
                                                            buttons = QMessageBox.Ok)
                    self.gnxAlert.emit(e)     
                db.conn.close()

    @Slot()
    def deleteCategory(self):
        sender = self.sender()
        data = sender.data()

        result = QMessageBox.question(self.window, "Delete Category", 
                                      "This will permanently delete this category and its contents.\nAre you sure you want to continue?", 
                                      QMessageBox.Cancel | QMessageBox.Yes, QMessageBox.Cancel)
        if result == QMessageBox.Yes:
            try:
                db = gnxDB()
                if db.conn == None:
                    return
            
                cur = db.conn.cursor()

                cur.execute("DELETE FROM categories WHERE parent = ? OR id = ?", [data["category"], data["category"]])
                db.conn.commit()

                # clean up
                while True:
                    cur.execute("DELETE FROM categories WHERE id IN \
                                    (SELECT c.id AS id FROM categories AS c \
                                        LEFT JOIN categories AS c2 ON c.parent = c2.id \
                                        WHERE c2.id IS NULL AND c.parent <> 0)")

                    db.conn.commit()
                    if cur.rowcount == 0:
                        break

                # delete all orphan patches
                cur.execute("DELETE FROM patches WHERE id IN \
                                (SELECT p.id AS id FROM patches AS p \
                                    LEFT JOIN categories AS c ON p.category = c.id \
                                    WHERE c.id IS NULL)")
                db.conn.commit()

                # remove from tree
                pcat = findByData(self.libHeader, data)
                p = pcat.index()
                self.model.removeRow(pcat.index().row(), pcat.index().parent())

            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Delete Category Error", \
                                                        text = f"Unable to delete category from database\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)     
            db.conn.close() 
            self.model.layoutChanged

    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        self.gnx.deviceConnectedChanged.connect(self.setConnected)
        self.gnx.gnxPatchNamesUpdated.connect(self.patchNamesUpdated)
        self.gnx.patchNameChanged.connect(self.setCurrentPatch)
        #self.gnx.midiPatchChange.connect(self.midiPatchChange)             # patch number may be mapped - do not use
        self.gnx.patch_added_to_library.connect(self.patchAdded)

    @Slot()
    def patchAdded(self, category, id, name, description, tags):          
        data = {"role": "header", "type": "library", "category": category} # look for parent category
        pcat = findByData(self.libHeader, data)
        add_patch_to_tree(tree = self.tree, model = self.model, parent = pcat, type = "library", patch_id = id,
                            name = name, description = description, tags = tags)
    @Slot()
    def itemChanged(self):
        pass

    @Slot()
    def dataChanged(self, topleft, bottomright, roles):
        if Qt.EditRole in roles:
            text = topleft.data(Qt.EditRole)
            data = topleft.data(Qt.UserRole)
            if data["role"] == "patch" and data["type"] == "user":

                if len(text) > 6:
                    text = text[0:6]
            
                bank = data["bank"]
                patch = data["patch"]

                w2 = self.model.itemFromIndex(topleft)
                w1 = self.model.itemFromIndex(topleft.siblingAtColumn(0))
                data["name"] = text
                w1.setData(data, Qt.UserRole)
                w2.setData(data, Qt.UserRole)

                self.gnx.save_patch(text, bank, patch, bank, patch)

            elif data["role"] == "patch" and data["type"] == "library":
                if len(text) > 6:
                    text = text[0:6]
                try:
                    db = gnxDB()
                    if db.conn == None:
                        return
                    db.conn.row_factory = sqlite3.Row
                    cur = db.conn.cursor()
                    cur.execute("UPDATE patches SET name=? WHERE id = ?", [text, data["patch"]])
                    db.conn.commit()
                except Exception as e:
                    e = GNXError(icon = QMessageBox.Critical, title = "Rename Patch Error", \
                                                            text = f"Unable to rename patch in database\n{e}", \
                                                            buttons = QMessageBox.Ok)
                    self.gnxAlert.emit(e)     
                db.conn.close()

                w1 = self.model.itemFromIndex(topleft)
                data["name"] = text
                w1.setData(data, Qt.UserRole)

            elif data["role"] == "header" and data["type"] == "library":
                try:
                    db = gnxDB()
                    if db.conn == None:
                        return
                    db.conn.row_factory = sqlite3.Row
                    cur = db.conn.cursor()
                    cur.execute("UPDATE categories SET name=? WHERE id = ?", [text, data["category"]])
                    db.conn.commit()
                except Exception as e:
                    e = GNXError(icon = QMessageBox.Critical, title = "Rename Category Error", \
                                                            text = f"Unable to rename category in database\n{e}", \
                                                            buttons = QMessageBox.Ok)
                    self.gnxAlert.emit(e)     
                db.conn.close()

                data["name"] = text
                topleft.setData(data, Qt.UserRole)

    @Slot()
    def midiPatchChange(self, parameter):
        bank = int(parameter / 48)
        patch = parameter % 48
        self.setPatchInTree(None, bank, patch, QModelIndex())

    @Slot()
    def selectionChangedEvent(self):

        for x in self.selection.selectedIndexes():

            if x.data() == None:    # click on LIBRARY chucks this out
                return

            data = x.data(Qt.UserRole)
            if data["role"] == "patch":
                bank = data["bank"]
                patch = data["patch"]
                if not self.blockPatchChange:
                    if data["type"] == "factory" or data["type"] == "user":
                        self.gnx.send_patch_change(bank, patch)
                        if self.patchDetailsGroupBox.height() > 0:
                            self.patchDetailsAnimationHide.start()
                    else:
                        if self.patchDetailsGroupBox.height() == 0:
                            self.patchDetailsAnimationShow.start()
                        self.setDescriptionAndTags(data)
            else:
                if self.patchDetailsGroupBox.height() > 0:
                    self.patchDetailsAnimationHide.start()
                pass
            break

        self.model.layoutChanged

    def setDescriptionAndTags(self, data):

        # set description and tags panels
        if data["role"] == "patch":
            if  data["type"] == "library":
                self.patchDescription.setPlainText(data["description"])
                self.patchTags.setPlainText(data["tags"])
                self.patchDescription.setEnabled(True)
                self.patchTags.setEnabled(True)
                self.patchUpdateButton.setEnabled(True)
            else:
                self.patchDescription.setPlainText("[No description]")
                self.patchTags.setPlainText("[No tags]")
                self.patchDescription.setEnabled(False)
                self.patchTags.setEnabled(False)
                self.patchUpdateButton.setEnabled(False)
        else:
            self.patchDescription.setPlainText("[No description]")
            self.patchTags.setPlainText("[No tags]")
            self.patchDescription.setEnabled(False)
            self.patchTags.setEnabled(False)
            self.patchUpdateButton.setEnabled(False)

        setattr(self.patchUpdateButton, "patchData", data)

    @Slot()
    def patchUpdateButtonClicked(self):
        sender = self.sender()
        data = getattr(sender, "patchData")

        description =  self.patchDescription.toPlainText()
        tags =  self.patchTags.toPlainText()

        try:
            db = gnxDB()
            if db.conn == None:
                return

            cur = db.conn.cursor()
            cur.execute("UPDATE patches SET description = ?, tags = ? WHERE id = ?", [description, tags, data["patch"]])
            db.conn.commit()
            db.conn.close()

            patch = findByData(self.libHeader, data)
            data["description"] = description
            data["tags"] = tags
            patch.setData(data, Qt.UserRole)

            self.setDescriptionAndTags(data)

        except Exception as e:
            e = GNXError(icon = QMessageBox.Critical, title = "Edit Patch Error", \
                                                    text = f"Unable to update patch in database\n{e}", \
                                                    buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)     

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
            add_patch_to_tree(tree = self.tree, model = self.model, parent = h, type = "factory" if bank == 0 else "user",
                               bank = bank, patch_num = k, name = n, description = None, tags = None)

            k += 1

        self.setHeaderSpanned(self.tree.model().invisibleRootItem())

    # all rows with children will span comlumns
    def setHeaderSpanned(self, parent):
        idx = parent.index()
        for row in range(parent.rowCount()):

            index1 = self.model.index(row, 0, idx)
            data1 = index1.data(Qt.UserRole)

            if parent.child(row, 0).hasChildren() or data1["role"] == "header":
                self.tree.setFirstColumnSpanned(row, idx, True)

            if parent.child(row, 0).hasChildren():
                self.setHeaderSpanned(parent.child(row, 0))
    
    def searchButtonClicked(self):
        text = self.patchSearchText.text()

        self.searchResults.clear()
        if len(text) > 0:
            groupAnimation = QSequentialAnimationGroup(self)
            if self.patchDetailsGroupBox.height() > 0:
                groupAnimation.addAnimation(self.patchDetailsAnimationHide)
            if self.searchResultsGroupBox.height() == 0:
                groupAnimation.addAnimation(self.searchResultsAnimationShow)
            
            groupAnimation.start()

            try:
                # search factory
                if self.factoryHeader.hasChildren():
                    for r in range(self.factoryHeader.rowCount()):
                        data = self.factoryHeader.child(r, 0).data(Qt.UserRole)
                        x = re.search(re.escape(text), data["name"], re.IGNORECASE)
                        if x:
                            self.searchResults.addPathLink("FACTORY>" + data["name"], f"0>{data["patch"]}")

                # search user
                if self.userHeader.hasChildren():
                    for r in range(self.userHeader.rowCount()):
                        data = self.userHeader.child(r, 0).data(Qt.UserRole)
                        x = re.search(re.escape(text), data["name"], re.IGNORECASE)
                        if x:
                            self.searchResults.addPathLink("USER>" + data["name"], f"1>{data["patch"]}")


                # search library
                db = gnxDB()
                if db.conn == None:
                    return
                db.conn.row_factory = sqlite3.Row
                wc = f"%{text}%"
                cur = db.conn.cursor()
                cur.execute("SELECT id, category, name FROM patches WHERE \
                                    name LIKE ? OR \
                                    description LIKE ? OR \
                                    tags LIKE ?", [wc, wc, wc])
                rc = cur.fetchall()
                prows = [dict(row) for row in rc]
                
                for p in prows:
                    # find parents
                    path, pathlink = self.getPatchPath(db, p["category"])
                    self.searchResults.addPathLink(f"LIBRARY>{path}{p["name"]}", f"2>{pathlink}{p["id"]}")

                db.conn.close()

            except Exception as e:
                e = GNXError(icon = QMessageBox.Critical, title = "Search Error", \
                                                        text = f"Unable to search patches\n{e}", \
                                                        buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)

        if self.searchResults.document().isEmpty():
            self.searchResults.setText("No matching results for this search.")
        
    def getPatchPath(self, db, id, path = "", pathlink = ""):
        if id == 0:
            return path, pathlink

        try:
            db = gnxDB()
            if db.conn == None:
                return

            db.conn.row_factory = sqlite3.Row
            cur = db.conn.cursor()
            cur.execute("SELECT parent, name FROM categories WHERE id = ?", [id])
            rc = cur.fetchone()
            if rc:
                path = f"{rc[1]}>{path}"
                pathlink = f"{id}>{pathlink}" 
                return self.getPatchPath(db, rc[0], path, pathlink)
            else:
                return path, pathlink
        except Exception as e:
            raise e
                
    def findAnchorInTree(self, anchor):
        self.tree.collapseAll()
        idx = self.gnxHeader.index()
        self.tree.expand(idx)

        path = anchor.split(">")

        if int(path[0]) == 0 or int(path[0]) == 1:    # factory or user
            idx = self.factoryHeader.index() if int(path[0]) == 0 else self.userHeader.index() 
            self.tree.expand(idx)
            patchid = int(path[1])

        elif int(path[0]) == 2:    # library
            idx = self.libHeader.index()
            self.tree.expand(idx)
            for cat in range(1, len(path) - 1):
                data = {"role": "header", "type": "library", "category": int(path[cat])}
                pitem = findByData(self.libHeader, data)
                idx = pitem.index()
                self.tree.expand(idx)

            patchid = int(path[-1])

        types = ["factory", "user", "library"]
        headers = [self.factoryHeader, self.userHeader, self.libHeader]
        data = {"role": "patch", "type": types[int(path[0])], "patch": patchid}
        pitem = findByData(headers[int(path[0])], data)
        if int(path[0]) in [0, 1]:
            patch = pitem.index().siblingAtColumn(1)
        else:
            patch = pitem.index()
        self.blockPatchChange = True
        self.tree.selectionModel().clearSelection()
        self.tree.selectionModel().clearCurrentIndex()
        self.tree.selectionModel().select(patch, QItemSelectionModel.ClearAndSelect)
        self.blockPatchChange = False

        self.tree.scrollTo(patch)
            
        pass
