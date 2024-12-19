# cabface.py
#
# GNX Edit Cabinet widget for Digitech GNX1
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
from PySide6.QtGui import QPainter, QImage, QAction, QColor, QPen, QFont

import sys
import os

from .cache import cache_image
from .styledial import StyleDial

class CabFace(QWidget):

    CAB_STYLES = {
        0  : {"name": "Cabinet Off",        "img": "cab_of", "size": 60, "x": 110, "y": 10, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        1  : {"name": "American 2x12",      "img": "am2x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        2  : {"name": "British 4x12",       "img": "br4x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x00, 0x00, 0x00),  "ticks": False, "marks": range(0, 11, 2)},
        3  : {"name": "Vintage 30 4x12",    "img": "v_4x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        4  : {"name": "British 2x12",       "img": "br2x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        5  : {"name": "American 1x12",      "img": "am1x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        6  : {"name": "Blonde 2x12",        "img": "bl2x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        7  : {"name": "Fane 4x12",          "img": "fn4x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xFF, 0xFF, 0xFF),  "ticks": True,  "marks": None},
        8  : {"name": "Greenback 4x12",     "img": "gr4x12", "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        9  : {"name": "User 1",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        10 : {"name": "User 2",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        11 : {"name": "User 3",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        12 : {"name": "User 4",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        13 : {"name": "User 5",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        14 : {"name": "User 6",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        15 : {"name": "User 7",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        16 : {"name": "User 8",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        17 : {"name": "User 9",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        18 : {"name": "Custom",             "img": "user",   "size": 60, "x": 110, "y": 44, "spacing": 100, "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None}
    }

    POTS = {
        "pot_tuning": {"minval": 0, "maxval": 48, "minunit": -12, "maxunit": 12, "prefix": "", "suffix":"", "dialmin": -12, "dialmax": 12, "dialstep": 4,
                       "format": "+0.1f"}
    }

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WA_StyledBackground)

        # can't programatically add pots because the get garbage collected so explicitly declared here
        self.pot_tuning = StyleDial(self)

        self.setCabStyle(0)

    def set_user_name(self, key, name):
        self.CAB_STYLES[key + 9]["name"] = name

    def setCabStyle(self, style):
        #print(f"Cab Style Requested: {style}")
        style = 0 if style == None else style
        self._cabStyle = style
        #print(f"CAB: {style}")

        if self._cabStyle in self.CAB_STYLES.keys():
            d = self.CAB_STYLES[self._cabStyle]
        else:
            d = self.CAB_STYLES[0]

        #img = cache_image(f"cab:{d["img"]}-cab.png", os.path.join(os.path.dirname(__file__), "images/cabface/", f"{d["img"]}-cab.png"))

        rect = self.geometry()
        w = 280
        self.setGeometry(rect.left(), rect.top(), w, w)
        self.setMaximumSize(w, w)
        self.setMinimumSize(w, w)
        self.fitPots()
        self.update()

    def cabStyle(self):
        return self._cabStyle

    def paintEvent(self, event):
        if self._cabStyle in self.CAB_STYLES.keys():
            k = self._cabStyle
        else:
            k = 0
            
        d = self.CAB_STYLES[k]

        img = cache_image(f"cab:{d["img"]}-cab.png", os.path.join(os.path.dirname(__file__), "images/cabface/", f"{d["img"]}-cab.png"))

        painter = QPainter(self)
        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)

        # insert name for user cabs
        if k > 8:
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(Qt.white)
            painter.setPen(pen)
            font = QFont("Arial")
            font.setPixelSize(20)
            font.setBold(True)
            font.setLetterSpacing(QFont.PercentageSpacing, 0)
            painter.setFont(font)
            painter.drawText(QRect(0, 0, w, h - 42), Qt.AlignCenter | Qt.AlignBottom, " " + d["name"].upper())

    def fitPots(self):
        if self._cabStyle in self.CAB_STYLES.keys():
            d = self.CAB_STYLES[self._cabStyle]
        else:
            d = self.CAB_STYLES[0]

        x = d["x"]
        for p in self.POTS.keys():
            if getattr(self, p) == None:
                setattr(self, p, StyleDial(self, d["img"]))
            else:
                getattr(self, p).setDialStyle(d["img"])

            getattr(self, p).setMaximum(self.POTS[p]["maxval"])
            getattr(self, p).setMinimum(self.POTS[p]["minval"])
            getattr(self, p).setMinimumUnit(self.POTS[p]["minunit"])
            getattr(self, p).setMaximumUnit(self.POTS[p]["maxunit"])
            getattr(self, p).setUnitPrefix(self.POTS[p]["prefix"])
            getattr(self, p).setUnitSuffix(self.POTS[p]["suffix"])
            getattr(self, p).setDialMinimum(self.POTS[p]["dialmin"])
            getattr(self, p).setDialMaximum(self.POTS[p]["dialmax"])
            getattr(self, p).setDialStep(self.POTS[p]["dialstep"])
            getattr(self, p).setToolTipFormat(self.POTS[p]["format"])
            getattr(self, p).setGeometry(x, d["y"], d["size"], d["size"])
            getattr(self, p).setImagePath(os.path.join(os.path.dirname(__file__), "images/dial"))

            getattr(self, p).setStartStop(d["start"])        
            getattr(self, p).setEndStop(d["end"])
            getattr(self, p).setOverallRotation(d["rotate"])

            getattr(self, p).setDrawStyle(d["ds"])
            getattr(self, p).setMarkerColor(d["color"])
            getattr(self, p).setTicks(d["ticks"])
            getattr(self, p).setMarks(d["marks"])

            x += d["spacing"]

    cabStyleChanged = Signal(int)

    @Slot()
    def contextMenuClicked(self):
        action = self.sender()
        k = action.data()
        if k != None:
            self.setCabStyle(k)
            self.cabStyleChanged.emit(k)
        pass

    def contextMenuEvent(self, event):
        # Create the context menu
        context_menu = QMenu(self)

        for k, cab in self.CAB_STYLES.items():

            n = cab["name"]
            action = QAction(n, self)
            action.setCheckable(True)
            action.setChecked(k == self._cabStyle)
 
            action.setData(k)
            action.triggered.connect(self.contextMenuClicked)
            context_menu.addAction(action)

        context_menu.addSeparator()  # Add a separator between options
        action = QAction("Cancel", self)
        context_menu.addAction(action)
        
        # Show the context menu at the position of the mouse click
        context_menu.exec_(event.globalPos())

    # properties for QT Creator plugin

    cabStyle = Property(int, cabStyle, setCabStyle)