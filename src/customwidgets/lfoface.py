# lfoface.py
#
# GNXEdit LFO widget for Digitech GNX1
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
from .factory import factory_expression_assignments

class LFOFace(QWidget):

    pot_speed = {"minval": 0, "maxval": 185, "minunit": 0, "maxunit": 185, "prefix": "", "suffix":"Hz", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 0, "y": 0, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": [x / 100.0 for x in range(5, 100, 1)] +  [x / 10.0 for x in range(10, 101, 1)], "tooltipformat": "0.2f" }

    pot_waveform = {"minval": 0, "maxval": 2, "minunit": 1, "maxunit": 3, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 0, "y": 0, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": False,  "marks": ["","",""],
                    "unitscale": ["Triangle", "Sine", "Square"], "tooltipformat": "s" }
    

    lfoChanged = Signal()
    lfoPotChanged = Signal(int, dict)    # parameter, pot

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 240)

        # selectors

        self.combobox_1 = self.makeCombo(292, 48, self.combobox_1_changed, "lfo1selector")
        self.combobox_2 = self.makeCombo(732, 48, self.combobox_2_changed, "lfo2selector")

        self.comboboxes = {
                            0: self.combobox_1,
                            1: self.combobox_2
        }

        # labels
        self.labels = {
            0: {"min": self.makeLabel(292, 102, "green"), "max": self.makeLabel(395, 102, "green"), "speed": self.makeLabel( 84, 102, "green"), "waveform": None},
            1: {"min": self.makeLabel(732, 102, "red"), "max": self.makeLabel(835, 102, "red"), "speed": self.makeLabel(524, 102, "red"), "waveform": None}
        }

        # pots

        self.pots = { 
            0: {"min": StyleDial(self), "max": StyleDial(self), "speed": StyleDial(self), "waveform": StyleDial(self)},
            1: {"min": StyleDial(self), "max": StyleDial(self), "speed": StyleDial(self), "waveform": StyleDial(self)}
        }

        self.pots[0]["min"].valueChanged.connect(self.updateLabel1)
        self.pots[0]["max"].valueChanged.connect(self.updateLabel2)
        self.pots[0]["speed"].valueChanged.connect(self.updateLabel3)
        self.pots[1]["min"].valueChanged.connect(self.updateLabel4)
        self.pots[1]["max"].valueChanged.connect(self.updateLabel5)
        self.pots[1]["speed"].valueChanged.connect(self.updateLabel6)


        self.pot_pos = {    
            0: {"min": {"x": 302, "y": 133}, "max": {"x": 406, "y": 133}, "speed": {"x":  94, "y": 133}, "waveform": {"x": 198, "y": 133}},
            1: {"min": {"x": 742, "y": 133}, "max": {"x": 846, "y": 133}, "speed": {"x": 534, "y": 133}, "waveform": {"x": 638, "y": 133}}
        }

        self._drawn = False

        self._types = {0: 0, 1: 0}        # factory_expression_assignments index

        self.fitPots()

        self.setMouseTracking(True)    # only track when mouse key pressed

        self.update()

    # notify expression device of pots formats
    def sendExpPots(self):
        self.lfoPotChanged.emit(0x04, self.pot_speed)
        self.lfoPotChanged.emit(0x05, self.pot_speed)

    @Slot()
    def devicePotChanged(self, section, parameter, pot, name):          # name = None set to '' by system
        for k, v in factory_expression_assignments.items():
            if v["section"] == section and v["parameter"] == parameter:
                factory_expression_assignments[k]["pot"] = pot
                if name == "":
                    self.hideComboboxItem(self.combobox_1, k, True)
                    self.hideComboboxItem(self.combobox_2, k, True)
                else:
                    self.hideComboboxItem(self.combobox_1, k, False)
                    self.hideComboboxItem(self.combobox_2, k, False)

                factory_expression_assignments[k]["name"] = name
                self.combobox_1.setItemText(k, name)
                self.combobox_2.setItemText(k, name)
        
        self.fitPots()

    def hideComboboxItem(self, combobox, index, hide):
        model = combobox.model()
        item = model.item(index)
        if hide:
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        else:
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
        view = combobox.view()
        view.setRowHidden(index, hide)

    def makeCombo(self, x, y, changed, name):
        combobox = QComboBox(self)
        combobox.setObjectName(name)
        combobox.setGeometry(x, y, 183, 28)
        for k, v in factory_expression_assignments.items():
            combobox.addItem(v["name"], k)
        combobox.currentIndexChanged.connect(changed)
        return combobox

    def makeLabel(self, x, y, color):
        label = QLabel("Label", parent = self )
        label.setGeometry(x, y, 80, 18)
        label.setFixedSize(80, 18)
        label.setProperty("cssClass", color)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop )
        return label
    
    def updateLabel(self, x, m):
        p = self.pots[x][m]
        value = p.value()
        if p.unitsScale == None:
            unitval = p.minimumUnit + (value * (p.maximumUnit - p.minimumUnit) / (p.maximum() - p.minimum()))
        else:
            unitval = p.unitsScale[value]
            
        fstr = "{0} {1:" + p.toolTipFormat + "} {2}"
        self.labels[x][m].setText(fstr.format(p.unitPrefix, unitval, p.unitSuffix))

    def updateLabel1(self):
        self.updateLabel(0, "min")
    
    def updateLabel2(self):
        self.updateLabel(0, "max")

    def updateLabel3(self):
        self.updateLabel(0, "speed")
    
    def updateLabel4(self):
        self.updateLabel(1, "min")

    def updateLabel5(self):
        self.updateLabel(1, "max")

    def updateLabel6(self):
        self.updateLabel(1, "speed")

    def combobox_1_changed(self, index):
        self._types[0] = index
        self.fitPots()
        self.update()
        self.lfoChanged.emit()

    def combobox_2_changed(self, index):
        self._types[1] = index
        self.fitPots()
        self.update()
        self.lfoChanged.emit()

    def fitPots(self):

        for x in range(0, 2):
            
            for m in ["min", "max", "speed", "waveform"]:
                if m in ["min", "max"]:
                    p = factory_expression_assignments[self._types[x]]["pot"]
                else:
                    if m == "speed":
                        p = self.pot_speed
                    else:
                        p = self.pot_waveform

                if p == None or len(p) == 0:        
                    self.pots[x][m].setVisible(False)
                else:

                    p["x"] =  self.pot_pos[x][m]["x"]
                    p["y"] =  self.pot_pos[x][m]["y"]

                    # some pots have parameters missing, amp and cab are set by type, but we just want direct style
                    p["img"] = "direct"
                    p["w"] = 60
                    p["h"] = 60

                    p["start"] = p["start"] if "start" in p else 45
                    p["end"] = p["end"] if "end" in p else 315
                    p["rotate"] = p["rotate"] if "rotate" in p else 180
                    p["ds"] = 2
                    p["color"] = Qt.black
                    p["ticks"] = True
                    p["marks"] = p["marks"] if "marks" in p else range(0,11)
                    p["unitscale"] = p["unitscale"] if "unitscale" in p else None
                    p["tooltipformat"] = p["tooltipformat"] if "tooltipformat" in p else "0.0f"

                    self.pots[x][m].setDialStyle(p["img"])

                    self.pots[x][m].setMaximum(p["maxval"])
                    self.pots[x][m].setMinimum(p["minval"])
                    self.pots[x][m].setMinimumUnit(p["minunit"])
                    self.pots[x][m].setMaximumUnit(p["maxunit"])
                    self.pots[x][m].setUnitPrefix(p["prefix"])
                    self.pots[x][m].setUnitSuffix(p["suffix"])
                    self.pots[x][m].setDialMinimum(p["dialmin"])
                    self.pots[x][m].setDialMaximum(p["dialmax"])
                    self.pots[x][m].setDialStep(p["dialstep"])
                    self.pots[x][m].setGeometry(p["x"], p["y"], p["w"], p["h"])
                    self.pots[x][m].setImagePath(os.path.join(os.path.dirname(__file__), "images/dial"))

                    self.pots[x][m].setStartStop(p["start"])        
                    self.pots[x][m].setEndStop(p["end"])
                    self.pots[x][m].setOverallRotation(p["rotate"])

                    self.pots[x][m].setDrawStyle(p["ds"])
                    self.pots[x][m].setMarkerColor(p["color"])
                    self.pots[x][m].setTicks(p["ticks"])
                    self.pots[x][m].setMarks(p["marks"])

                    self.pots[x][m].setUnitsScale(p["unitscale"])
                    self.pots[x][m].setToolTipFormat(p["tooltipformat"])

                if self._types[x] == 0 and m in ["min", "max"]:                 # off
                    self.pots[x][m].setVisible(False)
                    self.labels[x][m].setVisible(False)
                else:
                    if m != "waveform":
                        self.pots[x][m].setVisible(True)
                        self.pots[x][m].setVisible(True)
                        self.labels[x][m].setVisible(True)                    
                        self.updateLabel(x, m)

    def setLFOType0(self, value):
        self._types[0] = int(value)
        self.lfoChanged.emit()     # check emitted parameter

    def setLFOType1(self, value):
        self._types[1] = int(value)
        self.lfoChanged.emit()     # check emitted parameter

    def lfoType0(self):
        return self._type[0]
    
    def lfoType1(self):
        return self._type[1]
    
    # called when values received

    def setAssignment(self, lfo, index):
        self._types[lfo] = index
        self.comboboxes[lfo].blockSignals(True)
        self.comboboxes[lfo].setCurrentIndex(index)
        self.comboboxes[lfo].blockSignals(False)
        self.fitPots()
        self.update()

    def setParameters(self, lfos):
        for index, lfo in lfos.items():
            self.setAssignment(index, lfo["assignment"])
            self.pots[index]["speed"].setValue(lfo["speed"])
            self.updateLabel(index, "speed")
            self.pots[index]["waveform"].setValue(lfo["waveform"])
            #self.updateLabel(index, "waveform")
            self.pots[index]["min"].setValue(lfo["min"])
            self.updateLabel(index, "min")
            self.pots[index]["max"].setValue(lfo["max"])
            self.updateLabel(index, "max")

        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)

        png = "lfo-0.png"
        img = cache_image(f"lfo:{png}", os.path.join(os.path.dirname(__file__), "images/lfoface/", f"{png}"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)
        self._drawn = False

        for x in range(0, 2):
            png1 = f"lfo{x + 1}_label_bg.png"
            img1 = cache_image(f"lfo:{png1}", os.path.join(os.path.dirname(__file__), "images/lfoface/", f"{png1}"))
            for m in ["min", "max", "speed"]:
                label1 = self.labels[x][m]
                if m == "speed" or self._types[x] != 0:
                    painter.drawImage(QRect(label1.geometry().x() - 8, label1.geometry().y() - 8, img1.width(), img1.height()), img1)

            if self._types[x] != 0:
                png2 = f"lfo{x + 1}_label_m.png"
                img2 = cache_image(f"lfo:{png2}", os.path.join(os.path.dirname(__file__), "images/lfoface/", f"{png2}"))
                label2 = self.labels[x]["min"]
                painter.drawImage(QRect(label2.geometry().x(), label2.geometry().y() + 104, img2.width(), img2.height()), img2)

    @Slot()
    def contextMenuClicked(self):
        pass

    def contextMenuEvent(self, event):
        # Create the context menu
        pass

    # properties for QT Creator plugin

    lfoType0 = Property(int, lfoType0, setLFOType0)
    lfoType1 = Property(int, lfoType0, setLFOType1)
                         