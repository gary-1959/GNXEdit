# delayface.py
#
# CPGen Delay widget for Digitech GNX1
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

def pot_2_units():
    a = []
    for i in range(0, 100):
        a.append(f"{i:0.0f}")

    a.append("R-HOLD")
    return a

def pot_3_units():
    a = []
    for i in range(1, 100):
        a.append(f"{i:0.0f}")

    a.append("OFF")
    return a

def balance_units():
    a = []
    for i in range(-99, 100):
        if i < 0:
            a.append(f"L {abs(i):0.0f}")
        elif i > 0:
            a.append(f"{abs(i):0.0f} R")
        else:
            a.append(f"CENTRE")
    return a

class DelayFace(QWidget):

    POTS = {
        "pot_1": {"minval": 0, "maxval": 2000, "minunit": 0, "maxunit": 2000, "prefix": "", "suffix":"ms", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 100, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": pot_2_units(), "tooltipformat": "s" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": pot_3_units(), "tooltipformat": "s" },
        "pot_4": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_5": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_6": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 786, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    delayChanged = Signal(int, int)
    delayPotChanged = Signal(int, dict) # parameter, pot

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 240)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "delay_off.png", "on": "delay_on.png"}

        self.button_mono = None
        self.button_pingpong = None
        self.button_analog = None
        self.button_analogpong = None

        self.buttons = [
            "button_mono", "button_pingpong", "button_analog", "button_analogpong"
            ]
        x = 442
        for b in self.buttons:
            setattr(self, b, {"x": x, "y": 183, "w": 34, "h": 12, "off": "off.png", "on": "on.png"})
            x += 50

        # pots

        self.pot_1 = StyleDial(self)
        self.pot_2 = StyleDial(self)
        self.pot_3 = StyleDial(self)
        self.pot_4 = StyleDial(self)
        self.pot_5 = StyleDial(self)
        self.pot_6 = StyleDial(self)

        self._on = 0
        self._type = 0
        self._drawn = False
        self._param1 = 0
        self._param2 = 0
        self._param3 = 0
        self._param4 = 0
        self._param5 = 0
        self._param6 = 0

        self.fitPots()

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.update()

        self.sendExpPots()
        
    # notify expression device of pots formats
    def sendExpPots(self):
        self.delayPotChanged.emit(0x02, self.POTS["pot_1"])
        self.delayPotChanged.emit(0x03, self.POTS["pot_2"])
        self.delayPotChanged.emit(0x04, self.POTS["pot_3"])
        self.delayPotChanged.emit(0x05, self.POTS["pot_4"])
        self.delayPotChanged.emit(0x06, self.POTS["pot_5"])
        self.delayPotChanged.emit(0x07, self.POTS["pot_6"])

    def fitPots(self):
        pots = self.POTS
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

    def setDelayType(self, value):
        self._type = int(value)
        self.delayChanged.emit(0, value)

    def delayType(self):
        return self._type

    def setOn(self, value):
        self._on = value
        self.delayChanged.emit(1, value)

    def setParam1(self, value):
        self._param1 = value
        self.delayChanged.emit(2, value)

    def setParam2(self, value):
        self._param2 = value
        self.delayChanged.emit(3, value)

    def setParam3(self, value):
        self._param3 = value
        self.delayChanged.emit(4, value)

    def setParam4(self, value):
        self._param4 = value
        self.delayChanged.emit(5, value)

    def setParam5(self, value):
        self._param5 = value
        self.delayChanged.emit(6, value)

    def setParam6(self, value):
        self._param6 = value
        self.delayChanged.emit(7, value)

    def setDelay(self, type = None, on = None, param1 = None, param2 = None, param3 = None, param4 = None, param5 = None, param6 = None):
        self._on = on if on != None else self._on
        if type != None:
            if type != self._type:
                self._type = type 
                self.fitPots()
        self._param1 = param1 if param1 != None else self._param1
        self._param2 = param2 if param2 != None else self._param2
        self._param3 = param3 if param3 != None else self._param3
        self._param4 = param4 if param4 != None else self._param4
        self._param5 = param5 if param5 != None else self._param5
        self._param6 = param6 if param6 != None else self._param6
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)

        png = "delay-0.png"
        img = cache_image(f"delay:{png}", os.path.join(os.path.dirname(__file__), "images/delayface/", f"{png}"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)
        self._drawn = False

        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"delay:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/delayface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"delay:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/delayface/", f"{self.button_on["on"]}"))

        painter.drawImage(QRect(self.button_on["x"], self.button_on["y"], self.button_on["w"], self.button_on["h"]), d)

        # set buttons

        n = 0
        for bname in self.buttons:
            b = getattr(self, bname)
            if n == self._type:
                bimg = b["on"]
                img = cache_image(f"delay:{bimg}", os.path.join(os.path.dirname(__file__), "images/delayface/", bimg))
            else:
                bimg = b["off"]
                img = cache_image(f"delay:{bimg}", os.path.join(os.path.dirname(__file__), "images/delayface/", bimg))

            painter.drawImage(QRect(b["x"], b["y"], b["w"], b["h"]), img)
            n += 1

    # check x, y is inside button rectangle
    def inside_button(self, x, y, b):

        if x >= b["x"] and x <= (b["x"] + b["w"]) and y >= b["y"] and y <= (b["y"] + b["h"]):
            return True
        return False

    def mouseEvent(self, event):
        pos = event.localPos()
        buttons = event.buttons()

        # check it is inside button

        self.setCursor(Qt.ArrowCursor)

        if self.inside_button(pos.x(), pos.y(), self.button_on):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._on == 0:
                    self.setOn(1)
                else:
                    self.setOn(0)

        else:
            n = 0
            for bname in self.buttons:
                b = getattr(self, bname)
                if self.inside_button(pos.x(), pos.y(), b):
                    self.setCursor(Qt.PointingHandCursor)
                    if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                        if self._type != n:
                            self.setDelayType(n)
                            break
                n += 1

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

    delayType = Property(int, delayType, setDelayType)