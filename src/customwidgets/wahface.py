# wahface.py
#
# CPGen Wah widget for Digitech GNX1
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

from PySide6.QtWidgets import QWidget,  QWidget, QMenu, QMessageBox, QComboBox
from PySide6.QtCore import Qt, QRect, Property, Slot, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QImage, QAction, QColor, QPen, QFont

import sys
import os

from .cache import cache_image
from .styledial import StyleDial

class WahFace(QWidget):

    POTS = {
        "pot_min": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1) },
        "pot_max": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1)},
        "pot_pedal": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1)},
    }

    wahChanged = Signal(int, int)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 140)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "wah_off.png", "on": "wah_on.png"}
        self.button_cry = {"x": 202, "y": 45, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_boutique = {"x": 202, "y": 65, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_full = {"x": 202, "y": 85, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}

        # pots

        self.pot_min = StyleDial(self)
        self.pot_max = StyleDial(self)
        self.pot_pedal = StyleDial(self)

        self.fitPots()

        self._type = 0
        self._on = 0
        self._drawn = False

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.update()

    def fitPots(self):
        for p in self.POTS.keys():
            if getattr(self, p) == None:
                setattr(self, p, StyleDial(self, self.POTS[p]["img"]))
            else:
                getattr(self, p).setDialStyle(self.POTS[p]["img"])

            getattr(self, p).setMaximum(self.POTS[p]["maxval"])
            getattr(self, p).setMinimum(self.POTS[p]["minval"])
            getattr(self, p).setMinimumUnit(self.POTS[p]["minunit"])
            getattr(self, p).setMaximumUnit(self.POTS[p]["maxunit"])
            getattr(self, p).setUnitPrefix(self.POTS[p]["prefix"])
            getattr(self, p).setUnitSuffix(self.POTS[p]["suffix"])
            getattr(self, p).setDialMinimum(self.POTS[p]["dialmin"])
            getattr(self, p).setDialMaximum(self.POTS[p]["dialmax"])
            getattr(self, p).setDialStep(self.POTS[p]["dialstep"])
            getattr(self, p).setGeometry(self.POTS[p]["x"], self.POTS[p]["y"], self.POTS[p]["w"], self.POTS[p]["h"])
            getattr(self, p).setImagePath(os.path.join(os.path.dirname(__file__), "images/dial"))

            getattr(self, p).setStartStop(self.POTS[p]["start"])        
            getattr(self, p).setEndStop(self.POTS[p]["end"])
            getattr(self, p).setOverallRotation(self.POTS[p]["rotate"])

            getattr(self, p).setDrawStyle(self.POTS[p]["ds"])
            getattr(self, p).setMarkerColor(self.POTS[p]["color"])
            getattr(self, p).setTicks(self.POTS[p]["ticks"])
            getattr(self, p).setMarks(self.POTS[p]["marks"])

    def setType(self, value):
        self._type = value
        self.wahChanged.emit(0, value)

    def setOn(self, value):
        self._on = value
        self.wahChanged.emit(1, value)

    def setMin(self, value):
        self.wahChanged.emit(2, value)

    def setMax(self, value):
        self.wahChanged.emit(3, value)

    def setPedal(self, value):
        self.wahChanged.emit(4, value)

    def setWah(self, type = None, on = None, min = None, max = None, pedal = None):
        self._type = type if type != None else self._type
        self._on = on if on != None else self._on
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        if not self._drawn:
            png = "wah-001.png"
            img = cache_image(f"wah:{png}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{png}"))

            w = self.width()
            h = self.height()
            painter.drawImage(QRect(0, 0, w, h), img)
            self._drawn = False


        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"wah:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"wah:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_on["on"]}"))

        painter.drawImage(QRect(self.button_on["x"], self.button_on["y"], self.button_on["w"], self.button_on["h"]), d)

        match self._type:
            case 0: # cry
                c = cache_image(f"wah:{self.button_cry["on"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_cry["on"]}"))
                b = cache_image(f"wah:{self.button_boutique["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_boutique["off"]}"))
                f = cache_image(f"wah:{self.button_full["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_full["off"]}"))
            case 1: # boutique
                c = cache_image(f"wah:{self.button_cry["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_cry["off"]}"))
                b = cache_image(f"wah:{self.button_boutique["on"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_boutique["on"]}"))
                f = cache_image(f"wah:{self.button_full["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_full["off"]}"))
            case 2: # full
                c = cache_image(f"wah:{self.button_cry["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_cry["off"]}"))
                b = cache_image(f"wah:{self.button_boutique["off"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_boutique["off"]}"))
                f = cache_image(f"wah:{self.button_full["on"]}", os.path.join(os.path.dirname(__file__), "images/wahface/", f"{self.button_full["on"]}"))

        painter.drawImage(QRect(self.button_cry["x"], self.button_cry["y"], self.button_cry["w"], self.button_cry["h"]), c)
        painter.drawImage(QRect(self.button_boutique["x"], self.button_boutique["y"], self.button_boutique["w"], self.button_boutique["h"]), b)
        painter.drawImage(QRect(self.button_full["x"], self.button_full["y"], self.button_full["w"], self.button_full["h"]), f)
    
    # check x, y is inside button rectangle
    def inside_button(self, x, y, b):

        if x >= b["x"] and x <= (b["x"] + b["w"]) and y >= b["y"] and y <= (b["y"] + b["h"]):
            return True
        return False

    def mouseEvent(self, event):
        pos = event.localPos()
        buttons = event.buttons()

        # check it is inside button
        if self.inside_button(pos.x(), pos.y(), self.button_on):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._on == 0:
                    self.setOn(1)
                else:
                    self.setOn(0)

        elif self.inside_button(pos.x(), pos.y(), self.button_cry):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 0:
                    self.setType(0)

        elif self.inside_button(pos.x(), pos.y(), self.button_boutique):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 1:
                    self.setType(1)

        elif self.inside_button(pos.x(), pos.y(), self.button_full):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 2:
                    self.setType(2)
        else:
            pass
            self.setCursor(Qt.ArrowCursor)

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
