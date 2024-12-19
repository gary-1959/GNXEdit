# pickupface.py
#
# GNX Edit Pickup widget for Digitech GNX1
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

from PySide6.QtWidgets import QWidget,  QWidget, QMenu, QMessageBox
from PySide6.QtCore import Qt, QRect, Property, Slot, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QImage, QAction, QColor, QPen, QFont

import sys
import os

from .cache import cache_image

class PickupFace(QWidget):

    pickupChanged = Signal(int, int)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 140)

        # buttons

        self._button_direct = {"x": 223, "y": 15, "w": 115, "h": 112, "off": "direct_off.png", "on": "direct_on.png"}
        self._button_sc_hb  = {"x": 446, "y": 10, "w": 198, "h": 120, "off": "sc-hb_off.png", "on": "sc-hb_on.png"}
        self._button_hb_sc  = {"x": 699, "y": 12, "w": 197, "h": 118, "off": "hb-sc_off.png", "on": "hb-sc_on.png"}

        self._type = 0
        self._drawn = False

        self.setMouseTracking(True)    # only track when mouse key pressed

    def setType(self, value):
        self._type = value
        self.pickupChanged.emit(0, value)

    def setPickup(self, type = None):
        self._type = type if type != None else self._type
        print(f"PICKUP: Type: {self._type}")
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        if not self._drawn:
            png = "pickup-002.png"
            img = cache_image(f"pickup:{png}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{png}"))

            w = self.width()
            h = self.height()
            painter.drawImage(QRect(0, 0, w, h), img)
            self._drawn = False


        # set buttons
        match self._type:
            case 0: # direct
                d = cache_image(f"pickup:{self._button_direct["on"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_direct["on"]}"))
                s = cache_image(f"pickup:{self._button_sc_hb["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_sc_hb["off"]}"))
                h = cache_image(f"pickup:{self._button_hb_sc["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_hb_sc["off"]}"))
            case 1: # sc -> hb
                d = cache_image(f"pickup:{self._button_direct["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_direct["off"]}"))
                s = cache_image(f"pickup:{self._button_sc_hb["on"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_sc_hb["on"]}"))
                h = cache_image(f"pickup:{self._button_hb_sc["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_hb_sc["off"]}"))
            case 2: # hb -> sc
                d = cache_image(f"pickup:{self._button_direct["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_direct["off"]}"))
                s = cache_image(f"pickup:{self._button_sc_hb["off"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_sc_hb["off"]}"))
                h = cache_image(f"pickup:{self._button_hb_sc["on"]}", os.path.join(os.path.dirname(__file__), "images/pickupface/", f"{self._button_hb_sc["on"]}"))

        painter.drawImage(QRect(self._button_direct["x"], self._button_direct["y"], self._button_direct["w"], self._button_direct["h"]), d)
        painter.drawImage(QRect(self._button_sc_hb["x"], self._button_sc_hb["y"], self._button_sc_hb["w"], self._button_sc_hb["h"]), s)
        painter.drawImage(QRect(self._button_hb_sc["x"], self._button_hb_sc["y"], self._button_hb_sc["w"], self._button_hb_sc["h"]), h)
    
    # check x, y is inside button rectangle
    def inside_button(self, x, y, b):

        if x >= b["x"] and x <= (b["x"] + b["w"]) and y >= b["y"] and y <= (b["y"] + b["h"]):
            return True
        return False

    def mouseEvent(self, event):
        pos = event.localPos()
        buttons = event.buttons()

        # check it is inside button
        if self.inside_button(pos.x(), pos.y(), self._button_direct):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 0:
                    self.setType(0)

        elif self.inside_button(pos.x(), pos.y(), self._button_sc_hb):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 1:
                    self.setType(1)

        elif self.inside_button(pos.x(), pos.y(), self._button_hb_sc):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 2:
                    self.setType(2)

        # otherwise forbidden
        else:
            self.setCursor(Qt.ForbiddenCursor)
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.mouseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouseEvent(event)

    @Slot()
    def contextMenuClicked(self):
        pass

    def contextMenuEvent(self, event):
        # Create the context menu
        pass
