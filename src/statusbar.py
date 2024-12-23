# statusbar.py
#
# GNX Edit status bar handler
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

import settings

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QStatusBar, QLabel
from PySide6.QtCore import QFile, QIODevice, QCoreApplication, QDir, Slot, Signal, QObject

class StatusControl(QObject):

    def __init__(self, window = None, gnx = None):
        super().__init__()

        self.window = window
        self.gnx = gnx

        self.status_bar = self.window.findChild(QStatusBar, "statusBar")
        self.midi_channel_label = QLabel("MIDI Channel: --", self.status_bar)
        self.midi_channel_label.setToolTip("GNX MIDI channel number")
        self.status_bar.addPermanentWidget(self.midi_channel_label)

        self.gnx_connected_label = QLabel("\u2b24", self.status_bar)
        self.gnx_connected_label.setToolTip("Connected status")
        self.gnx_connected_label.setObjectName("gnxConnectedLabel")
        self.setConnected(False)
        self.status_bar.addPermanentWidget(self.gnx_connected_label)
        self.setMIDIChannel(0)
        
        self.patch_label = QLabel("Current Patch: --", self.status_bar)
        self.gnx_connected_label.setToolTip("Current patch")
        self.status_bar.addPermanentWidget(self.patch_label)

        if self.gnx != None:
            self.setGNX(gnx)

    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        gnx.deviceConnectedChanged.connect(self.setConnected)
        gnx.midiChannelChanged.connect(self.setMIDIChannel)
        gnx.patchNameChanged.connect(self.patchNameChanged)

    @Slot()
    def setConnected(self, connected):
        if connected:
            self.gnx_connected_label.setStyleSheet("color: green;")
        else:
            self.gnx_connected_label.setStyleSheet("color: red;")

    @Slot()
    def setMIDIChannel(self, channel):
        self.midi_channel_label.setText(f"MIDI Channel: {channel:02.0f}")

    @Slot()
    def patchNameChanged(self, name, bank, patch):
        banks = {0: "FACTORY", 1: "USER"}
        self.patch_label.setText(f"Current Patch: {name} [{banks[bank]}:{(patch + 1):02.0f}]")
