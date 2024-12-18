# menu.py
#
# CPGen menu handler
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

from PySide6.QtCore import Slot, Signal, QObject
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMenu, QMenuBar, QComboBox
from PySide6.QtCore import QFile, QIODevice, Qt

class MenuHandler():

    def __init__(self, window, midicontrol):
        self.window = window
        self.midicontrol = midicontrol

        menubar = window.findChild(QMenuBar, "mainMenuBar")

        # FILE menu       
        file_menu = menubar.findChild(QMenu, "menuFile")
        for a in file_menu.actions():
            n = a.objectName()
            match n:
                case "actionQuit":
                    a.triggered.connect(window.close)
                case _:
                    print(f"Unrecognised menu option {n}")
            pass

        # MIDI menu       
        midi_menu = menubar.findChild(QMenu, "menuMIDI")
        for a in midi_menu.actions():
            n = a.objectName()
            match n:
                case "actionMIDIInterface":
                    a.triggered.connect(self.midicontrol.openMIDIDialog)
                case _:
                    print(f"Unrecognised menu option {n}")
            pass


    


