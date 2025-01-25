# menu.py
#
# GNXEdit menu handler
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
from PySide6.QtWidgets import QMenu, QMenuBar, QComboBox, QMessageBox
from PySide6.QtCore import QFile, QIODevice, Qt

import common
from help import get_help

class MenuHandler():

    def __init__(self, window = None, midicontrol = None, gnx = None):
        self.window = window
        self.midicontrol = midicontrol

        self.menubar = window.findChild(QMenuBar, "mainMenuBar")

        # FILE menu       
        file_menu = self.menubar.findChild(QMenu, "menuFile")
        for a in file_menu.actions():
            n = a.objectName()
            match n:
                case "actionQuit":
                    a.triggered.connect(self.window.close)
                case _:
                    if not a.isSeparator():
                         print(f"Unrecognised FILE menu option {n}")
            pass

        # MIDI menu       
        midi_menu = self.menubar.findChild(QMenu, "menuMIDI")
        for a in midi_menu.actions():
            n = a.objectName()
            match n:
                case "actionMIDIInterface":
                    a.triggered.connect(self.midicontrol.openMIDIDialog)
                case _:
                    if not a.isSeparator():
                        print(f"Unrecognised MIDI menu option {n}")
            pass

        # help menu       
        help_menu = self.menubar.findChild(QMenu, "menuHelp")
        for a in help_menu.actions():
            n = a.objectName()
            match n:
                case "actionAbout":
                    a.triggered.connect(self.about)
                case "actionHelp":
                    a.triggered.connect(self.help)
                case _:
                    if not a.isSeparator():
                        print(f"Unrecognised HELP menu option {n}")
            pass

        if gnx != None:
            self.setGNX()

    def about(self):
        QMessageBox.about(self.window, "About GNXEdit", common.ABOUT_TEXT)

    def help(self):
        get_help()

    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        self.setDeviceMenu()
        
        # Device menu    
    def setDeviceMenu(self):   
        device_menu = self.menubar.findChild(QMenu, "menuDevice")
        device_menu.aboutToShow.connect(self.deviceMenuAboutToShow)
        for a in device_menu.actions():
            n = a.objectName()
            match n:
                case "actionResync":
                    a.triggered.connect(self.gnx.midi_resync)
                case "actionSaveAmp":
                    a.triggered.connect(self.gnx.save_amp_to_gnx)
                case "actionSaveAmpToLibrary":
                    a.triggered.connect(self.saveAmpToLibrary)
                case "actionSavePatch":
                    a.triggered.connect(self.gnx.save_patch_to_gnx)
                case "actionSavePatchToLibrary":
                    a.triggered.connect(self.savePatchToLibrary)
                case _:
                    if not a.isSeparator():
                        print(f"Unrecognised Device menu option {n}")

            pass

    def savePatchToLibrary(self):
        self.gnx.save_patch_to_library("patch")
    
    def saveAmpToLibrary(self):
        self.gnx.save_patch_to_library("amp")

    def deviceMenuAboutToShow(self):
        device_menu = self.menubar.findChild(QMenu, "menuDevice")
        for a in device_menu.actions():
            n = a.objectName()
            if n in ["actionSavePatch", "actionSavePatchToLibrary"]:
                a.setEnabled(self.gnx.has_patch())
        pass

    


