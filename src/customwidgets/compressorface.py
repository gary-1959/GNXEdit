# compressorface.py
#
# GNX Edit Compressor widget for Digitech GNX1
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

from PySide6.QtWidgets import QWidget,  QWidget, QLabel
from PySide6.QtCore import Qt, QRect, Slot, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QImage, QAction, QColor, QPen, QFont

import sys
import os

from .cache import cache_image
from .styledial import StyleDial
from GNX1 import factory_compressor_ratio

class CompressorFace(QWidget):

    NOPOTS = {  # for expression assignment
        "pot_attack": {"minval": 0, "maxval": 2, "minunit": 0, "maxunit": 2, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(0,3,1),
                    "unitscale": ["Fast", "Medium", "Slow"], "tooltipformat": "s" }
    }

    POTS = {
        "pot_ratio": {"minval": 0, "maxval": 11, "minunit": 0, "maxunit": 11, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": factory_compressor_ratio, "tooltipformat": "s" },
        "pot_threshold": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_gain": {"minval": 0, "maxval": 20, "minunit": 0, "maxunit": 20, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    compressorChanged = Signal(int, int)
    compressorPotChanged = Signal(int, dict)    # parameter, pot

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 140)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "compressor_off.png", "on": "compressor_on.png"}
        self.button_fast = {"x": 202, "y": 45, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_medium = {"x": 202, "y": 65, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_slow = {"x": 202, "y": 85, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}

        # pots

        self.pot_ratio = StyleDial(self)
        self.pot_ratio.valueChanged.connect(self.updateLabel1)
        self.pot_threshold = StyleDial(self)
        self.pot_gain = StyleDial(self)

        # labels

        self.label_1 = self.makeLabel(359, 12)

        self._attack = 0
        self._on = 0
        self._drawn = False

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.fitPots()

        self.updateLabel1()

        self.update()

    # notify expression device of pots formats
    def sendExpPots(self):
        self.compressorPotChanged.emit(0x02, self.NOPOTS["pot_attack"])
        self.compressorPotChanged.emit(0x03, self.POTS["pot_ratio"])
        self.compressorPotChanged.emit(0x04, self.POTS["pot_threshold"])
        self.compressorPotChanged.emit(0x05, self.POTS["pot_gain"])

    def makeLabel(self, x, y):
        label = QLabel("Label", parent = self )
        label.setGeometry(x, y, 84, 13)
        label.setFixedSize(84, 18)
        label.setProperty("cssClass", "orange")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop )
        return label
    
    def updateLabel1(self):
        self.updateLabel(self.pot_ratio, self.label_1)

    def updateLabel(self, p, l):
        value = p.value()
        if p.unitsScale != None:
            unitval = p.unitsScale[value]
            
            fstr = "{0} {1:" + p.toolTipFormat + "} {2}"
            l.setText(fstr.format(p.unitPrefix, unitval, p.unitSuffix))

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

            getattr(self, p).setUnitsScale(self.POTS[p]["unitscale"])
            getattr(self, p).setToolTipFormat(self.POTS[p]["tooltipformat"])

        self.sendExpPots()

    def setAttack(self, value):
        self._attack = value
        self.compressorChanged.emit(2, value)

    def setOn(self, value):
        self._on = value
        self.compressorChanged.emit(1, value)

    def setRatio(self, value):
        self.compressorChanged.emit(3, value)

    def setThreshold(self, value):
        self.compressorChanged.emit(4, value)

    def setGain(self, value):
        self.compressorChanged.emit(5, value)

    def setCompressor(self, type = None, attack = None, on = None, ratio = None, threshold = None, gain = None):
        self._attack = attack if attack != None else self._attack
        self._on = on if on != None else self._on
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        if not self._drawn:
            png = "compressor-001.png"
            img = cache_image(f"compressor:{png}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{png}"))

            w = self.width()
            h = self.height()
            painter.drawImage(QRect(0, 0, w, h), img)
            self._drawn = False


        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"compressor:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"compressor:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_on["on"]}"))

        painter.drawImage(QRect(self.button_on["x"], self.button_on["y"], self.button_on["w"], self.button_on["h"]), d)

        match self._attack:
            case 0: # fast
                f = cache_image(f"compressor:{self.button_fast["on"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_fast["on"]}"))
                m = cache_image(f"compressor:{self.button_medium["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_medium["off"]}"))
                s = cache_image(f"compressor:{self.button_slow["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_slow["off"]}"))
            case 1: # medium
                f = cache_image(f"compressor:{self.button_fast["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_fast["off"]}"))
                m = cache_image(f"compressor:{self.button_medium["on"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_medium["on"]}"))
                s = cache_image(f"compressor:{self.button_slow["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_slow["off"]}"))
            case 2: # slow
                f = cache_image(f"compressor:{self.button_fast["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_fast["off"]}"))
                m = cache_image(f"compressor:{self.button_medium["off"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_medium["off"]}"))
                s = cache_image(f"compressor:{self.button_slow["on"]}", os.path.join(os.path.dirname(__file__), "images/compressorface/", f"{self.button_slow["on"]}"))

        painter.drawImage(QRect(self.button_fast["x"], self.button_fast["y"], self.button_fast["w"], self.button_fast["h"]), f)
        painter.drawImage(QRect(self.button_medium["x"], self.button_medium["y"], self.button_medium["w"], self.button_medium["h"]), m)
        painter.drawImage(QRect(self.button_slow["x"], self.button_slow["y"], self.button_slow["w"], self.button_slow["h"]), s)
    
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

        elif self.inside_button(pos.x(), pos.y(), self.button_fast):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._attack != 0:
                    self.setAttack(0)

        elif self.inside_button(pos.x(), pos.y(), self.button_medium):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._attack != 1:
                    self.setAttack(1)

        elif self.inside_button(pos.x(), pos.y(), self.button_slow):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._attack != 2:
                    self.setAttack(2)
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
