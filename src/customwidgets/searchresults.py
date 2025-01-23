# pickupface.py
#
# GNXEdit Search results widget for Digitech GNX1
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

from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QColor

import sys
import os


from .cache import cache_image

class SearchResults(QTextEdit):

    owner = None

    def setOwner(self, owner):
        self.owner = owner

    def mousePressEvent(self, e):
        anchor = self.anchorAt(e.pos())
        if anchor:
            self.owner.findAnchorInTree(anchor)

    def mouseMoveEvent(self, e):
        anchor = self.anchorAt(e.pos())
        if anchor:
            self.viewport().setCursor(Qt.PointingHandCursor)
            pass
        else:
            self.viewport().setCursor(Qt.ArrowCursor)
            pass

    def addPathLink(self, path, pathlink):
        cursor = self.textCursor()
        fmt = cursor.charFormat()
        fmt.setForeground(QColor('blue'))
        fmt.setAnchor(True)
        fmt.setAnchorHref(pathlink)
        fmt.setToolTip(f"Click to follow {pathlink}")
        cursor.insertText(path + "\n", fmt)

