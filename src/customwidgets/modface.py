# modface.py
#
# GNX Edit Chorus/Modulation widget for Digitech GNX1
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

class ModFace(QWidget):

    CHORUS_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 0, "maxunit": 98, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit": 0, "maxunit": 98, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 19, "minunit": 1, "maxunit": 20, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 20, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 2, "minunit": 1, "maxunit": 3, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": False,  "marks": ["","",""],
                    "unitscale": ["Triangle", "Sine", "Square"], "tooltipformat": "s" },
        "pot_5": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_6": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 786, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }

    FLANGER_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit":1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 20, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 2, "minunit": 1, "maxunit": 3, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": False,  "marks": ["","",""],
                    "unitscale": ["Triangle", "Sine", "Square"], "tooltipformat": "s" },
        "pot_5": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_6": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 786, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    TFLANGER_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit":1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 20, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    TREMELO_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit":0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 2, "minunit": 1, "maxunit": 3, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": False,  "marks": ["","",""],
                    "unitscale": ["Triangle", "Sine", "Square"], "tooltipformat": "s" },
    }
    VIBRATO_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit":1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 2, "minunit": 1, "maxunit": 3, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": -45, "end": 45, "rotate": 0, "ds": 2, "color": Qt.black,  "ticks": False,  "marks": ["","",""],
                    "unitscale": ["Triangle", "Sine", "Square"], "tooltipformat": "s" },
    }
    ROTARY_POTS = {
        "pot_1": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit":0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 130, "minunit": 200, "maxunit": 1500, "prefix": "", "suffix":"Hz", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 578, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": None,
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_5": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_6": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 786, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    AUTOYA_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 49, "minunit": 1, "maxunit": 50, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 576, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_5": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    YAYA_POTS = {
        "pot_1": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 49, "minunit": 1, "maxunit": 50, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 576, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_5": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    SYNTH_POTS = {
        "pot_1": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 99, "minunit": 1, "maxunit": 100, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_4": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 576, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_5": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 682, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    ENVELOPE_POTS = {
        "pot_1": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 98, "minunit": 1, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_3": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_4": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 576, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    DETUNE_POTS = {
        "pot_1": {"minval": 0, "maxval": 48, "minunit": -24, "maxunit": 24, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    PITCH_POTS = {
        "pot_1": {"minval": 0, "maxval": 36, "minunit": -12, "maxunit": 24, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 266, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
        "pot_2": {"minval": 0, "maxval": 198, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 370, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,12,1),
                    "unitscale": balance_units(), "tooltipformat": "s" },
        "pot_3": {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 10, "dialstep": 1, "img": "direct",
                    "x": 474, "y": 36, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": None, "tooltipformat": "0.0f" },
    }
    modChanged = Signal(int, int)
    modPotChanged = Signal(int, dict, int)  # parameter, pot, type

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setGeometry(0, 0, 1000, 240)

        # buttons

        self.button_on = {"x": 103, "y": 53, "w": 34, "h": 34, "off": "mod_off.png", "on": "mod_on.png"}

        self.button_chorus = None
        self.button_flanger = None
        self.button_phaser = None
        self.button_tflanger = None
        self.button_tphaser = None
        self.button_tremelo = None
        self.button_panner = None
        self.button_vibrato = None
        self.button_rotary = None
        self.button_autoya = None
        self.button_yaya = None
        self.button_synth = None
        self.button_envelope = None
        self.button_detune = None
        self.button_pitch = None

        self.buttons = [
            "button_chorus", "button_flanger", "button_phaser", "button_tflanger", "button_tphaser", "button_tremelo",
            "button_panner", "button_vibrato", "button_rotary", "button_autoya", "button_yaya", "button_synth", "button_envelope",
            "button_detune", "button_pitch"
            ]
        x = 172
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

    # notify expression device of pots formats
    def sendExpPots(self):
        match self._type:
            case 0: # chorus
                self.modPotChanged.emit(0x02, self.CHORUS_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.CHORUS_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.CHORUS_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, self.CHORUS_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, self.CHORUS_POTS["pot_6"], self._type)
            case 1: # flanger
                self.modPotChanged.emit(0x02, self.FLANGER_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.FLANGER_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.FLANGER_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, self.FLANGER_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, self.FLANGER_POTS["pot_6"], self._type)
            case 2: # phaser (same as flanger)
                self.modPotChanged.emit(0x02, self.FLANGER_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.FLANGER_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.FLANGER_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, self.FLANGER_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, self.FLANGER_POTS["pot_6"], self._type)
            case 3: # triggered flanger
                self.modPotChanged.emit(0x02, self.TFLANGER_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.TFLANGER_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.TFLANGER_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.TFLANGER_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 4: # triggered phaser (same as triggered flanger)
                self.modPotChanged.emit(0x02, self.TFLANGER_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.TFLANGER_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.TFLANGER_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.TFLANGER_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 5: # tremelo
                self.modPotChanged.emit(0x02, self.TREMELO_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.TREMELO_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, None, self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 6: # panner (same as tremelo)
                self.modPotChanged.emit(0x02, self.TREMELO_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.TREMELO_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, None, self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 7: # vibrato (same as tremelo)
                self.modPotChanged.emit(0x02, self.TREMELO_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.TREMELO_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, None, self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 8: # rotary
                self.modPotChanged.emit(0x02, self.ROTARY_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.ROTARY_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.ROTARY_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.ROTARY_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, self.ROTARY_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, self.ROTARY_POTS["pot_6"], self._type)
            case 9: # auto ya
                self.modPotChanged.emit(0x02, self.AUTOYA_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.AUTOYA_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.AUTOYA_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.AUTOYA_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, self.AUTOYA_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 10: # ya ya
                self.modPotChanged.emit(0x02, self.YAYA_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.YAYA_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.YAYA_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.YAYA_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, self.YAYA_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 11: # synthtalk
                self.modPotChanged.emit(0x02, self.SYNTH_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.SYNTH_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.SYNTH_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.SYNTH_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, self.SYNTH_POTS["pot_5"], self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 12: # envelope
                self.modPotChanged.emit(0x02, self.ENVELOPE_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.ENVELOPE_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.ENVELOPE_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, self.ENVELOPE_POTS["pot_4"], self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 13: # detune
                self.modPotChanged.emit(0x02, self.DETUNE_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.DETUNE_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.DETUNE_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)
            case 14: # pitch
                self.modPotChanged.emit(0x02, self.PITCH_POTS["pot_1"], self._type)
                self.modPotChanged.emit(0x03, self.PITCH_POTS["pot_2"], self._type)
                self.modPotChanged.emit(0x04, self.PITCH_POTS["pot_3"], self._type)
                self.modPotChanged.emit(0x05, None, self._type)
                self.modPotChanged.emit(0x06, None, self._type)
                self.modPotChanged.emit(0x07, None, self._type)    

    def fitPots(self):
        match self._type:
            case 0: # chorus
                pots = self.CHORUS_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(True)
            case 1: # flanger
                pots = self.FLANGER_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(True)
            case 2: # phaser (same as flanger)
                pots = self.FLANGER_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(True)
            case 3: # triggered flanger
                pots = self.TFLANGER_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 4: # triggered phaser (same as triggered flanger)
                pots = self.TFLANGER_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 5: # tremelo
                pots = self.TREMELO_POTS
                self.pot_4.setVisible(False)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 6: # panner (same as tremelo)
                pots = self.TREMELO_POTS
                self.pot_4.setVisible(False)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 7: # vibrato (same as tremelo)
                pots = self.VIBRATO_POTS
                self.pot_4.setVisible(False)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 8: # rotary
                pots = self.ROTARY_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(True)
            case 9: # auto ya
                pots = self.AUTOYA_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(False)
            case 10: # ya ya
                pots = self.YAYA_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(False)
            case 11: # synth talk
                pots = self.SYNTH_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(True)
                self.pot_6.setVisible(False)
            case 12: # envelope
                pots = self.ENVELOPE_POTS
                self.pot_4.setVisible(True)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 13: # detune
                pots = self.DETUNE_POTS
                self.pot_4.setVisible(False)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case 14: # pitch
                pots = self.PITCH_POTS
                self.pot_4.setVisible(False)
                self.pot_5.setVisible(False)
                self.pot_6.setVisible(False)
            case _:
                pots = self.CHORUS_POTS

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


    def setModType(self, value):
        self._type = int(value)
        self.fitPots()
        self.modChanged.emit(0, value)

    def modType(self):
        return self._type

    def setOn(self, value):
        self._on = value
        self.modChanged.emit(1, value)

    def setParam1(self, value):
        self._param1 = value
        self.modChanged.emit(2, value)

    def setParam2(self, value):
        self._param2 = value
        self.modChanged.emit(3, value)

    def setParam3(self, value):
        self._param3 = value
        self.modChanged.emit(4, value)

    def setParam4(self, value):
        self._param4 = value
        self.modChanged.emit(5, value)

    def setParam5(self, value):
        self._param5 = value
        self.modChanged.emit(6, value)

    def setParam6(self, value):
        self._param6 = value
        self.modChanged.emit(7, value)

    def setMod(self, type = None, on = None, param1 = None, param2 = None, param3 = None, param4 = None, param5 = None, param6 = None):
        self._on = on if on != None else self._on
        if type != None:
            if type != self._type:
                self._type = type 
                self.fitPots()
        self._param1 = param1 if param1 != None else self._param1
        self._param2 = param2 if param2 != None else self._param2
        self._param3 = param3 if param3 != None else self._param3
        self._param4 = param4 if param4 != None else self._param4
        self._param5 = param5 if param4 != None else self._param5
        self._param6 = param6 if param4 != None else self._param6
        self.update()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        
        png = f"modface-{self._type}.png"
        img = cache_image(f"mod:{png}", os.path.join(os.path.dirname(__file__), "images/modface/", f"{png}"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img)
        self._drawn = False

        # set buttons
        match self._on:
            case 0: # off
                d = cache_image(f"mod:{self.button_on["off"]}", os.path.join(os.path.dirname(__file__), "images/modface/", f"{self.button_on["off"]}"))
            case 1: # on
                d = cache_image(f"mod:{self.button_on["on"]}", os.path.join(os.path.dirname(__file__), "images/modface/", f"{self.button_on["on"]}"))

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
                            self.setModType(n)
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

    modType = Property(int, modType, setModType)