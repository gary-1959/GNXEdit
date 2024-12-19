# warpface.py
#
# GNX Edit Warp widget for Digitech GNX1
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

class WarpFace(QWidget):

    NOPOTS = {  # for expression assignment
        "pot_channel": {"minval": 0, "maxval": 2, "minunit": 0, "maxunit": 2, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(0,3,1),
                    "unitscale": ["Green", "Red", "Warped"], "tooltipformat": "s" },
        "pot_amp_warp": {"minval": 0, "maxval": 99, "minunit": 1, "maxunit": 100, "prefix": "", "suffix":"", "dialmin": 0, "dialmax": 99, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(0,11),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_cab_warp": {"minval": 0, "maxval": 99, "minunit": 1, "maxunit": 100, "prefix": "", "suffix":"", "dialmin": 0, "dialmax": 99, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(0,11),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_warp": {"minval": 0, "maxval": 99, "minunit": 1, "maxunit": 100, "prefix": "", "suffix":"", "dialmin": 0, "dialmax": 99, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(0,11),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    warpChanged = Signal(int, int)
    warpPotChanged = Signal(int, dict)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 280, 280)

        self._warpBox = {"x": 60, "y": 60, "w": 160, "h": 160}
        self._origin = {"x": self._warpBox["x"] + (self._warpBox["w"] / 2), "y": self._warpBox["y"] + (self._warpBox["h"] / 2)}
        self._scale = 1.25
        self._cursorSize = 8
        self._cursor_x = 0
        self._cursor_y = 0

        # buttons

        self._button_green  = {"x": 63, "y": 253, "w": 34, "h": 12, "off": "green_off.png", "on": "green_on.png"}
        self._button_yellow = {"x": 123, "y": 253, "w": 34, "h": 12, "off": "yellow_off.png", "on": "yellow_on.png"}
        self._button_red    = {"x": 183, "y": 253, "w": 34, "h": 12, "off": "red_off.png", "on": "red_on.png"}

        self._type = 0
        self._amp_select = 0
        self._amp_warp = self._cab_warp = 50
        self._warpD = 0
        self._drawn = False

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.sendExpPots()

    # notify expression device of pots formats
    def sendExpPots(self):
        self.warpPotChanged.emit(0x01, self.NOPOTS["pot_channel"])
        self.warpPotChanged.emit(0x02, self.NOPOTS["pot_amp_warp"])
        self.warpPotChanged.emit(0x03, self.NOPOTS["pot_cab_warp"])
        self.warpPotChanged.emit(0x04, self.NOPOTS["pot_warp"])

    def setAmpSelect(self, value):
        self._amp_select = value
        self.warpChanged.emit(1, value)

    def setAmpWarp(self, value):
        value = 0 if value < 0 else value
        value = 99 if value > 99 else value
        self._amp_warp = value
        self.warpChanged.emit(2, value)

    def setCabWarp(self, value):
        value = 0 if value < 0 else value
        value = 99 if value > 99 else value
        self._cab_warp = value
        self.warpChanged.emit(3, value)

    def setWarpFactor(self, type = None, amp_select = None, amp_warp = None, cab_warp = None, warpD = None):
        self._type = type if type != None else self._type

        self._amp_select = amp_select if amp_select != None else self._amp_select # 0: green, 1: red, 2: yellow
        self._amp_warp = amp_warp if amp_warp != None else self._amp_warp # amp warp: 0 = max green, 99 = max red
        self._cab_warp = cab_warp if cab_warp != None else self._cab_warp # cab warp: 0 = max green, 99 = max red
        self._warpD = warpD if warpD != None else self._warpD

        print(f"WARP: Type: {self._type} Amp Select: {self._amp_select}, Amp Warp: {self._amp_warp}, C: {self._cab_warp}, D: {self._warpD}")

        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        if not self._drawn:
            png = "warp-001.png"
            img = cache_image(f"warp:{png}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{png}"))

            w = self.width()
            h = self.height()
            painter.drawImage(QRect(0, 0, w, h), img)
            self._drawn = False

        # add cursor if yellow selected

        if self._amp_select == 2:
            pen = QPen(Qt.black, 2, Qt.SolidLine)
            painter.setPen(pen)

            # Draw a rectangle
            self._cursor_x = self._origin["x"] + (self._scale * (self._cab_warp - 50))   # cab left-right (green / red)
            self._cursor_y = self._origin["y"] + (self._scale * (self._amp_warp - 50))   # amp up-down (green / red)
            
            painter.drawRect(self._cursor_x - (self._cursorSize / 2), self._cursor_y - (self._cursorSize / 2), self._cursorSize, self._cursorSize)  # x, y, width, height
            painter.drawLine(self._cursor_x - self._cursorSize, self._cursor_y, self._cursor_x  + self._cursorSize, self._cursor_y)
            painter.drawLine(self._cursor_x, self._cursor_y - self._cursorSize, self._cursor_x,  self._cursor_y + self._cursorSize)

        # set buttons
        match self._amp_select:
            case 0: # green
                g = cache_image(f"warp:{self._button_green["on"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_green["on"]}"))
                r = cache_image(f"warp:{self._button_red["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_red["off"]}"))
                y = cache_image(f"warp:{self._button_yellow["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_yellow["off"]}"))
            case 1: # red
                g = cache_image(f"warp:{self._button_green["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_green["off"]}"))
                r = cache_image(f"warp:{self._button_red["on"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_red["on"]}"))
                y = cache_image(f"warp:{self._button_yellow["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_yellow["off"]}"))
            case 2: #yellow
                g = cache_image(f"warp:{self._button_green["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_green["off"]}"))
                r = cache_image(f"warp:{self._button_red["off"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_red["off"]}"))
                y = cache_image(f"warp:{self._button_yellow["on"]}", os.path.join(os.path.dirname(__file__), "images/warpface/", f"{self._button_yellow["on"]}"))

        painter.drawImage(QRect(self._button_green["x"], self._button_green["y"], self._button_green["w"], self._button_green["h"]), g)
        painter.drawImage(QRect(self._button_red["x"], self._button_red["y"], self._button_red["w"], self._button_red["h"]), r)
        painter.drawImage(QRect(self._button_yellow["x"], self._button_yellow["y"], self._button_yellow["w"], self._button_yellow["h"]), y)
    
    # check x, y is inside button rectangle
    def inside_button(self, x, y, b):

        if x >= b["x"] and x <= (b["x"] + b["w"]) and y >= b["y"] and y <= (b["y"] + b["h"]):
            return True
        return False

    def mouseEvent(self, event):
        pos = event.localPos()
        buttons = event.buttons()

        # check it is inside warp window
        if pos.x() >= self._warpBox["x"] and \
            pos.x() <= (self._warpBox["x"] + self._warpBox["w"]) and \
            pos.y() >= self._warpBox["y"] and \
            pos.y() <= (self._warpBox["y"] + self._warpBox["h"]):

            self.setCursor(Qt.CrossCursor)

            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                self.setCursor(Qt.SizeAllCursor)

                cab_warp = 50 + (pos.x() - self._origin["x"]) / self._scale
                self.setCabWarp(cab_warp)

                amp_warp = 50 + (pos.y() - self._origin["y"]) / self._scale
                self.setAmpWarp(amp_warp)

                print(f"Position: {pos.x()}, {pos.y()} Left Button: {buttons & Qt.LeftButton}")
            else:
                self.setCursor(Qt.CrossCursor)

        elif self.inside_button(pos.x(), pos.y(), self._button_green):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._amp_select != 0:
                    self.setAmpSelect(0)

        elif self.inside_button(pos.x(), pos.y(), self._button_red):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._amp_select != 1:
                    self.setAmpSelect(1)

        elif self.inside_button(pos.x(), pos.y(), self._button_yellow):
            self.setCursor(Qt.PointingHandCursor)
            if buttons & Qt.LeftButton or buttons & Qt.RightButton:
                if self._amp_select != 2:
                    self.setAmpSelect(2)

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
