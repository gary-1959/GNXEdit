# ampface.py
#
# GNXEdit Amp widget for Digitech GNX1
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

class AmpFace(QWidget):

    AMP_STYLES = {
        0 :  {"name": "Direct",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "direct", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        1 :  {"name": "Blackface",      "size": 60, "spacing": 104, "x": 166, "y": 24, "img": "blkfac", "start":0,  "end": 300, "rotate": 0,   "ds": 1, "color": Qt.lightGray,              "ticks": False, "marks": None},
        2 :  {"name": "Boutique",       "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "boutiq", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        3 :  {"name": "Dual Rectifier", "size": 60, "spacing": 104, "x": 166, "y": 24, "img": "rectif", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        4 :  {"name": "Hotrod",         "size": 60, "spacing": 104, "x": 166, "y": 24, "img": "hotrod", "start":0,  "end": 300, "rotate": 0,   "ds": 1, "color": Qt.lightGray,              "ticks": False, "marks": None},
        5 :  {"name": "Tweed",          "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "tweed",  "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xFF, 0xFF, 0xFF),  "ticks": True,  "marks": None},
        6 :  {"name": "British Combo",  "size": 60, "spacing": 104, "x": 148, "y": 48, "img": "brtcmb", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xD1, 0xD1, 0x61),  "ticks": True,  "marks": None},
        7 :  {"name": "Clean Tube",     "size": 60, "spacing": 104, "x": 148, "y": 48, "img": "clntub", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xC8, 0xC8, 0xC8),  "ticks": True,  "marks": None},
        8 :  {"name": "British Stack",  "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "brtstk", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x00, 0x00, 0x00),  "ticks": False, "marks": range(0, 11, 2)},
        9 :  {"name": "Tube Crunch",    "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "crunch", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xF9, 0xF9, 0xF9),  "ticks": True,  "marks": None},
        10 : {"name": "High Gain",      "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "higain", "start":45, "end": 345, "rotate": 180, "ds": 2, "color": QColor(0x00, 0x00, 0x00),  "ticks": False,  "marks": range(0, 12)},
        11 : {"name": "Blues",          "size": 60, "spacing": 104, "x": 166, "y": 24, "img": "blues",  "start":30, "end": 330, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": False,  "marks": range(1, 13)},
        12 : {"name": "Modern Gain",    "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "modgan", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x00, 0x00, 0x00),  "ticks": True,  "marks": range(0, 11, 2)},
        13 : {"name": "Fuzz",           "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "fuzz",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x00, 0x00, 0x00),  "ticks": True,  "marks": None},
        14 : {"name": "Bassman",        "size": 60, "spacing": 104, "x": 166, "y": 24, "img": "bassmn", "start":0,  "end": 300, "rotate": 0,   "ds": 1, "color": Qt.lightGray,              "ticks": False, "marks": None},
        15 : {"name": "Hi Watt",        "size": 60, "spacing": 104, "x": 103, "y": 43, "img": "hiwatg", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xFF, 0xFF, 0xFF),  "ticks": True, "marks": range(0, 11, 2)},
        16 : {"name": "Acoustic",       "size": 60, "spacing": 104, "x": 148, "y": 48, "img": "acoust", "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0xD1, 0xC0, 0x61),  "ticks": True,  "marks": None},
        17 : {"name": "User 1",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        18 : {"name": "User 2",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        19 : {"name": "User 3",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        20 : {"name": "User 4",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        21 : {"name": "User 5",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        22 : {"name": "User 6",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        23 : {"name": "User 7",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        24 : {"name": "User 8",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None},
        25 : {"name": "User 9",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None },
        26 : {"name": "Custom",         "size": 60, "spacing": 104, "x": 103, "y": 31, "img": "user",   "start":45, "end": 315, "rotate": 180, "ds": 2, "color": QColor(0x88, 0x88, 0x88),  "ticks": True,  "marks": None }
    }   

    POTS = {
        "pot_gain": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_bass_freq": {"minval": 0, "maxval": 250, "minunit": 50, "maxunit": 300, "prefix": "", "suffix":"Hz", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_bass_level": {"minval": 0, "maxval": 24, "minunit": -12, "maxunit": 12, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_mid_freq": {"minval": 0, "maxval": 4700, "minunit": 300, "maxunit": 5000, "prefix": "", "suffix":"Hz", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_mid_level": {"minval": 0, "maxval": 24, "minunit": -12, "maxunit": 12, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_treble_freq": {"minval": 0, "maxval": 7500, "minunit": 500, "maxunit": 8000, "prefix": "", "suffix":"Hz", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_treble_level": {"minval": 0, "maxval": 24, "minunit": -12, "maxunit": 12, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1},
        "pot_level": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1}
    }

    ampStyleChanged = Signal(int)
    ampPotChanged = Signal(int, dict)

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WA_StyledBackground)

        # can't programatically add pots because the get garbage collected so explicitly declared here
        self.pot_gain = StyleDial(self)
        self.pot_bass_freq = StyleDial(self)
        self.pot_bass_level = StyleDial(self)
        self.pot_mid_freq = StyleDial(self)
        self.pot_mid_level = StyleDial(self)
        self.pot_treble_freq = StyleDial(self)
        self.pot_treble_level = StyleDial(self)
        self.pot_level = StyleDial(self)

        self.setAmpStyle(0)

    # notify expression device of pots formats
    def sendExpPots(self):
        self.ampPotChanged.emit(0x01, self.POTS["pot_gain"])
        self.ampPotChanged.emit(0x08, self.POTS["pot_level"])

    def set_user_name(self, key, name):
        self.AMP_STYLES[key + 17]["name"] = name

    def setAmpStyle(self, style):
        #print(f"Amp Style Requested: {style}")
        style = 0 if style == None else style
        self._ampStyle = style
        #print(f"AMP: {style}")

        if self._ampStyle in self.AMP_STYLES.keys():
            d = self.AMP_STYLES[self._ampStyle]
        else:
            d = self.AMP_STYLES[0]

        img = cache_image(f"amp:{d["img"]}-amp.png", os.path.join(os.path.dirname(__file__), "images/ampface/", f"{d["img"]}-amp.png"))

        rect = self.geometry()
        self.setGeometry(rect.left(), rect.top(), img.width(), img.height())
        self.setMaximumSize(img.width(), img.height())
        self.setMinimumSize(img.width(), img.height())

        self.fitPots()
        self.update()

    def ampStyle(self):
        return self._ampStyle

    def paintEvent(self, event):

        if self._ampStyle in self.AMP_STYLES.keys():
            k = self._ampStyle
        else:
            k = 0
            
        d = self.AMP_STYLES[k]

        img = cache_image(f"amp:{d["img"]}-amp.png", os.path.join(os.path.dirname(__file__), "images/ampface/", f"{d["img"]}-amp.png"))

        painter = QPainter(self)
        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)

        # insert name for user amps
        if k > 16:
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(QColor(0x44, 0x44, 0x44))
            painter.setPen(pen)
            font = QFont("Arial")
            font.setPixelSize(26)
            font.setBold(True)
            font.setLetterSpacing(QFont.PercentageSpacing, 170)
            painter.setFont(font)
            painter.drawText(QRect(0, 0, w, h - 6), Qt.AlignCenter | Qt.AlignBottom, " " + d["name"].upper())

    def fitPots(self):

        if self._ampStyle in self.AMP_STYLES.keys():
            d = self.AMP_STYLES[self._ampStyle]
        else:
            d = self.AMP_STYLES[0]
    
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

        self.sendExpPots()

    @Slot()
    def contextMenuClicked(self):
        action = self.sender()
        k = action.data()
        if k != None:
            self.setAmpStyle(k)
            self.ampStyleChanged.emit(k)
        pass

    def contextMenuEvent(self, event):
        # Create the context menu
        context_menu = QMenu(self)

        action = QAction("SELECT AMP")
        action.setProperty("class", "context-menu-title")
        action.setDisabled(True)
        action.triggered.connect(self.contextMenuClicked)
        context_menu.addAction(action)
        x = context_menu.actions()
        context_menu.addSeparator()

        for k, amp in self.AMP_STYLES.items():
            n = amp["name"]

            action = QAction(n, self)
            action.setCheckable(True)
            action.setChecked(k == self._ampStyle)

            action.setData(k)
            action.triggered.connect(self.contextMenuClicked)
            context_menu.addAction(action)

        context_menu.addSeparator()  # Add a separator between options
        action = QAction("Cancel", self)
        context_menu.addAction(action)
        
        # Show the context menu at the position of the mouse click
        context_menu.exec_(event.globalPos())

    # properties for QT Creator plugin

    ampStyle = Property(int, ampStyle, setAmpStyle)