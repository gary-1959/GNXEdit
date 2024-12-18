# whammyface.py
#
# CPGen Whammy/IPS widget for Digitech GNX1
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
from GNX1 import factory_whammy_shift, factory_ips_shift, factory_ips_key, factory_ips_scale

class WhammyFace(QWidget):

    WHAMMY_POTS = {
        "pot_1": {"minval": 0, "maxval": 15, "minunit": 0, "maxunit": 15, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 15, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": None,
                    "unitscale": factory_whammy_shift, "tooltipformat": "s" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    IPS_POTS = {
        "pot_1": {"minval": 0, "maxval": 13, "minunit": 0, "maxunit": 13, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 14, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": None,
                    "unitscale": factory_ips_shift, "tooltipformat": "s" },
        "pot_2": {"minval": 0, "maxval": 5, "minunit": 0, "maxunit": 5, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 6, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": None,
                    "unitscale": factory_ips_scale, "tooltipformat": "s" },
        "pot_3": {"minval": 0, "maxval": 11, "minunit": 0, "maxunit": 11, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": None,
                    "unitscale": factory_ips_key, "tooltipformat": "s" },
        "pot_4": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    DETUNE_POTS = {
        "pot_1": {"minval": 0, "maxval": 24, "minunit": 0, "maxunit": 24, "prefix": "", "suffix":"", "dialmin": -24, "dialmax": 24, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(-24, 25, 2),
                    "unitscale": range(-24, 25, 2), "tooltipformat": "+0.0f" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    PITCH_POTS = {
        "pot_1": {"minval": 0, "maxval": 48, "minunit": 0, "maxunit": 48, "prefix": "", "suffix":"", "dialmin": -24, "dialmax": 24, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(-24, 25, 4),
                    "unitscale": range(-24, 25), "tooltipformat": "+0.0f" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    whammyChanged = Signal(int, int)
    whammyPotChanged = Signal(int, dict, int)   # parameter, pot, type

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 140)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "whammy_off.png", "on": "whammy_on.png"}
        self.button_whammy = {"x": 202, "y": 34, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_ips = {"x": 202, "y": 54, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_detune = {"x": 202, "y": 74, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}
        self.button_pitch = {"x": 202, "y": 94, "w": 34, "h": 12, "off": "off.png", "on": "on.png"}

        # pots

        self.pot_1 = StyleDial(self)
        self.pot_1.valueChanged.connect(self.updateLabel1)
        self.pot_2 = StyleDial(self)
        self.pot_2.valueChanged.connect(self.updateLabel2)
        self.pot_3 = StyleDial(self)
        self.pot_3.valueChanged.connect(self.updateLabel3)
        self.pot_4 = StyleDial(self)

        # labels

        self.label_1 = self.makeLabel(359, 12)
        self.label_2 = self.makeLabel(463, 12)
        self.label_3 = self.makeLabel(567, 12)

        self._on = 0
        self._type = 0
        self._drawn = False
        self._param1 = 0
        self._param2 = 0
        self._param3 = 0
        self._param4 = 0

        self.fitPots()

        self.updateLabel1()
        self.updateLabel2()
        self.updateLabel3()

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.update()

    # notify expression device of pots formats
    # type is 0 in startup
    def sendExpPots(self):
        match self._type:
            case 0: # Whammy
                self.whammyPotChanged.emit(0x02, self.WHAMMY_POTS["pot_1"], self._type)
                self.whammyPotChanged.emit(0x03, self.WHAMMY_POTS["pot_2"], self._type)
                self.whammyPotChanged.emit(0x04, self.WHAMMY_POTS["pot_3"], self._type) 
                self.whammyPotChanged.emit(0x05, None, self._type) 
            case 1: # IPS
                self.whammyPotChanged.emit(0x02, self.IPS_POTS["pot_1"], self._type)
                self.whammyPotChanged.emit(0x03, self.IPS_POTS["pot_2"], self._type)  
                self.whammyPotChanged.emit(0x04, self.IPS_POTS["pot_3"], self._type)
                self.whammyPotChanged.emit(0x05, self.IPS_POTS["pot_4"], self._type) 
            case 2: # Detune
                self.whammyPotChanged.emit(0x02, self.DETUNE_POTS["pot_1"], self._type)
                self.whammyPotChanged.emit(0x03, self.DETUNE_POTS["pot_2"], self._type)  
                self.whammyPotChanged.emit(0x04, None, self._type)
                self.whammyPotChanged.emit(0x05, None, self._type) 
            case 3: # Pitch
                self.whammyPotChanged.emit(0x02, self.PITCH_POTS["pot_1"], self._type)
                self.whammyPotChanged.emit(0x03, self.PITCH_POTS["pot_2"], self._type)  
                self.whammyPotChanged.emit(0x04, None, self._type)
                self.whammyPotChanged.emit(0x05, None, self._type) 

    def makeLabel(self, x, y):
        label = QLabel("Label", parent = self )
        label.setGeometry(x, y, 84, 13)
        label.setFixedSize(84, 18)
        label.setProperty("cssClass", "blue")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop )
        return label

    def updateLabel1(self):
        self.updateLabel(self.pot_1, self.label_1)

    def updateLabel2(self):
        self.updateLabel(self.pot_2, self.label_2)

    def updateLabel3(self):
        self.updateLabel(self.pot_3, self.label_3)

    def updateLabel(self, p, l):
        value = p.value()
        if p.unitsScale != None:
            unitval = p.unitsScale[value]
            
            fstr = "{0} {1:" + p.toolTipFormat + "} {2}"
            l.setText(fstr.format(p.unitPrefix, unitval, p.unitSuffix))

    def fitPots(self):
        match self._type:
            case 0: # whammy
                pots = self.WHAMMY_POTS
                self.pot_3.setVisible(True)
                self.pot_4.setVisible(False)

                self.label_1.setVisible(True)
                self.label_2.setVisible(False)
                self.label_3.setVisible(False)

            case 1: # ips
                pots = self.IPS_POTS
                self.pot_3.setVisible(True)
                self.pot_4.setVisible(True)

                self.label_1.setVisible(True)
                self.label_2.setVisible(True)
                self.label_3.setVisible(True)

            case 2: # detune
                pots = self.DETUNE_POTS
                self.pot_3.setVisible(False)
                self.pot_4.setVisible(False)

                self.label_1.setVisible(True)
                self.label_2.setVisible(False)
                self.label_3.setVisible(False)

            case 3: # pitch
                pots = self.PITCH_POTS
                self.pot_3.setVisible(False)
                self.pot_4.setVisible(False)

                self.label_1.setVisible(True)
                self.label_2.setVisible(False)
                self.label_3.setVisible(False)

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

    def setWhammyType(self, value):
        self._type = int(value)
        self.fitPots()
        self.updateLabel1()
        self.updateLabel2()
        self.updateLabel3()
        self.whammyChanged.emit(0, value)

    def whammyType(self):
        return self._type

    def setOn(self, value):
        self._on = value
        self.whammyChanged.emit(1, value)

    def setParam1(self, value):
        self._param1 = value
        self.whammyChanged.emit(2, value)

    def setParam2(self, value):
        self._param2 = value
        self.whammyChanged.emit(3, value)

    def setParam3(self, value):
        self._param3 = value
        self.whammyChanged.emit(4, value)

    def setParam4(self, value):
        self._param4 = value
        self.whammyChanged.emit(5, value)

    def setWhammy(self, type = None, on = None, param1 = None, param2 = None, param3 = None, param4 = None):
        self._on = on if on != None else self._on
        if type != None:
            if type != self._type:
                self._type = type 
                self.fitPots()
        self._param1 = param1 if param1 != None else self._param1
        self._param2 = param2 if param2 != None else self._param2
        self._param3 = param3 if param3 != None else self._param3
        self._param4 = param4 if param4 != None else self._param4
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        png = f"whammy-{self._type}.png"
        img = cache_image(f"whammy:{png}", os.path.join(os.path.dirname(__file__), "images/whammyface/", f"{png}"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)
        self._drawn = False

        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"whammy:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/whammyface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"whammy:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/whammyface/", f"{self.button_on["on"]}"))

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

        elif self.inside_button(pos.x(), pos.y(), self.button_whammy):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 0:
                    self.setWhammyType(0)

        elif self.inside_button(pos.x(), pos.y(), self.button_ips):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 1:
                    self.setWhammyType(1)

        elif self.inside_button(pos.x(), pos.y(), self.button_detune):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 2:
                    self.setWhammyType(2)

        elif self.inside_button(pos.x(), pos.y(), self.button_pitch):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._type != 3:
                    self.setWhammyType(3)

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

    whammyType = Property(int, whammyType, setWhammyType)