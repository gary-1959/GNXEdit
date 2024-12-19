# gateface.py
#
# GNX Edit Noise Gate widget for Digitech GNX1
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

from PySide6.QtWidgets import QWidget,  QWidget, QMenu, QMessageBox, QComboBox, QLabel
from PySide6.QtCore import Qt, QRect, Property, Slot, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QImage, QAction, QColor, QPen, QFont

import sys
import os

from .cache import cache_image
from .styledial import StyleDial

class GateFace(QWidget):

    SILENCER_POTS = {
        "pot_1": {"minval": 0, "maxval": 40, "minunit": 0, "maxunit": 40, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 9, "minunit": 0, "maxunit": 9, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" }
        }

    PLUCK_POTS = {
        "pot_1": {"minval": 0, "maxval": 40, "minunit": 0, "maxunit": 40, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 9, "minunit": 0, "maxunit": 9, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" }
    }

    gateChanged = Signal(int, int)
    gatePotChanged = Signal(int, dict, int)      # parameter, pot, type

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 140)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "gate_off.png", "on": "gate_on.png"}
        self.button_silencer = {"x": 202, "y": 54, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_pluck = {"x": 202, "y": 74, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}

        # pots

        self.pot_1 = StyleDial(self)
        self.pot_2 = StyleDial(self)
        self.pot_3 = StyleDial(self)

        self._on = 0
        self._type = 0
        self._drawn = False
        self._param1 = 0
        self._param2 = 0
        self._param3 = 0

        self.fitPots()

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.update()

    # notify expression device of pots formats
    def sendExpPots(self):
        match self._type:
            case 0: # silencer
                self.gatePotChanged.emit(0x02, self.SILENCER_POTS["pot_1"], self._type)
                self.gatePotChanged.emit(0x03, self.SILENCER_POTS["pot_2"], self._type)
                self.gatePotChanged.emit(0x04, None, self._type)
            case 1: # pluck
                self.gatePotChanged.emit(0x02, self.PLUCK_POTS["pot_1"], self._type)
                self.gatePotChanged.emit(0x03, self.PLUCK_POTS["pot_2"], self._type)
                self.gatePotChanged.emit(0x04, self.PLUCK_POTS["pot_3"], self._type)

    def fitPots(self):
        match self._type:
            case 0: # silencer
                pots = self.SILENCER_POTS
                self.pot_3.setVisible(False)

            case 1: # pluck
                pots = self.PLUCK_POTS
                self.pot_3.setVisible(True)

        for p in pots.keys():
            if getattr(self, p) == None:
                setattr(self, p, StyleDial(self, pots[p]["img"]))
            else:
                getattr(self, p).setDialStyle(pots[p]["img"])

            getattr(self, p).setMaximum(pots[p]["maxval"])
            getattr(self, p).setMinimum(pots[p]["minval"])
            getattr(self, p).setMinimumUnit(pots[p]["minunit"])
            getattr(self, p).setMaximumUnit(pots[p]["maxunit"])
            getattr(self, p).setUnitPrefix(pots[p]["prefix"])
            getattr(self, p).setUnitSuffix(pots[p]["suffix"])
            getattr(self, p).setDialMinimum(pots[p]["dialmin"])
            getattr(self, p).setDialMaximum(pots[p]["dialmax"])
            getattr(self, p).setDialStep(pots[p]["dialstep"])
            getattr(self, p).setGeometry(pots[p]["x"], pots[p]["y"], pots[p]["w"], pots[p]["h"])
            getattr(self, p).setImagePath(os.path.join(os.path.dirname(__file__), "images/dial"))

            getattr(self, p).setStartStop(pots[p]["start"])        
            getattr(self, p).setEndStop(pots[p]["end"])
            getattr(self, p).setOverallRotation(pots[p]["rotate"])

            getattr(self, p).setDrawStyle(pots[p]["ds"])
            getattr(self, p).setMarkerColor(pots[p]["color"])
            getattr(self, p).setTicks(pots[p]["ticks"])
            getattr(self, p).setMarks(pots[p]["marks"])

            getattr(self, p).setUnitsScale(pots[p]["unitscale"])
            getattr(self, p).setToolTipFormat(pots[p]["tooltipformat"])

        self.sendExpPots()

    def setGateType(self, value):
        self._type = int(value)
        self.fitPots()
        self.gateChanged.emit(0, value)

    def gateType(self):
        return self._type

    def setOn(self, value):
        self._on = value
        self.gateChanged.emit(1, value)

    def setParam1(self, value):
        self._param1 = value
        self.gateChanged.emit(2, value)

    def setParam2(self, value):
        self._param1 = value
        self.gateChanged.emit(3, value)

    def setParam3(self, value):
        self._param1 = value
        self.gateChanged.emit(4, value)

    def setGate(self, type = None, on = None, param1 = None, param2 = None, param3 = None):
        self._on = on if on != None else self._on
        if type != None:
            if type != self._type:
                self._type = type 
                self.fitPots()
        self._param1 = param1 if param1 != None else self._param1
        self._param2 = param2 if param2 != None else self._param2
        self._param3 = param3 if param3 != None else self._param3
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        png = f"gate-{self._type}.png"
        img = cache_image(f"gate:{png}", os.path.join(os.path.dirname(__file__), "images/gateface/", f"{png}"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)
        self._drawn = False

        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"gate:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/gateface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"gate:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/gateface/", f"{self.button_on["on"]}"))

        painter.drawImage(QRect(self.button_on["x"], self.button_on["y"], self.button_on["w"], self.button_on["h"]), d)

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

        elif self.inside_button(pos.x(), pos.y(), self.button_silencer):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 0:
                    self.setGateType(0)

        elif self.inside_button(pos.x(), pos.y(), self.button_pluck):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 1:
                    self.setGateType(1)

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

    # properties for QT Creator plugin

    gateType = Property(int, gateType, setGateType)