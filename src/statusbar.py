# statusbar.py
#
# GNXEdit status bar handler
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
from PySide6.QtCore import QFile, QIODevice, QCoreApplication, QDir, Slot, Signal, QObject, Qt

class StatusControl(QObject):
    connected = False
    resync = True
    uploading = 0
    watchdog = True

    def __init__(self, window = None, gnx = None):
        super().__init__()

        self.window = window
        self.gnx = gnx
        self.status_bar = self.window.findChild(QStatusBar, "statusBar")
        
        # uploading
        self.uploading_label = QLabel("UPLOADING", self.status_bar)
        self.uploading_label.setToolTip("Uploading to GNX1 Status")
        self.status_bar.addPermanentWidget(self.uploading_label)

        # resyncing
        self.resync_label = QLabel("RESYNC", self.status_bar)
        self.resync_label.setToolTip("Resync Status")
        self.status_bar.addPermanentWidget(self.resync_label)

        # watchdog
        self.watchdog_label = QLabel("WATCHDOG", self.status_bar)
        self.watchdog_label.setToolTip("Watchdog Status")
        self.status_bar.addPermanentWidget(self.watchdog_label)

        # MIDI channel
        self.midi_channel_label = QLabel("MIDI Channel: --", self.status_bar)
        self.midi_channel_label.setToolTip("GNX MIDI channel number")
        self.status_bar.addPermanentWidget(self.midi_channel_label)

        # connected status
        self.gnx_connected_label = QLabel("\u2b24", self.status_bar)
        self.gnx_connected_label.setToolTip("Connected status")
        self.gnx_connected_label.setObjectName("gnxConnectedLabel")
        self.setConnected(False)
        self.status_bar.addPermanentWidget(self.gnx_connected_label)
        self.setMIDIChannel(0)
        
        # patch number
        self.patch_label = QLabel("Current Patch: --", self.status_bar)
        self.gnx_connected_label.setToolTip("Current patch")
        self.status_bar.addPermanentWidget(self.patch_label)

        if self.gnx != None:
            self.setGNX(gnx)

        self.busy = False
        self.setBusyIndicator()

    # to set gnx after init
    def setGNX(self, gnx):
        self.gnx = gnx
        gnx.deviceConnectedChanged.connect(self.setConnected)
        gnx.midiChannelChanged.connect(self.setMIDIChannel)
        gnx.patchNameChanged.connect(self.patchNameChanged)
        gnx.resyncChanged.connect(self.setResync)
        gnx.uploadChanged.connect(self.setUploading)
        gnx.watchDogBite.connect(self.setWatchdog)

    def setBusyIndicator(self):
        app = QApplication.instance()
        if self.watchdog or self.uploading > 0 or self.resync:
            if not self.busy:
                app.setOverrideCursor(Qt.WaitCursor)
                self.busy = True
        else:
            if self.busy:
                app.restoreOverrideCursor()
                self.busy = False

    @Slot()
    def setWatchdog(self, watchdog):
        if not watchdog:
            self.watchdog_label.setText(f"WATCHDOG")
            self.watchdog_label.setStyleSheet("color: gray;")
        else:
            self.watchdog_label.setText(f"WATCHDOG")
            self.watchdog_label.setStyleSheet("color: red;")

        self.watchdog = watchdog
        self.setBusyIndicator()

    @Slot()
    def setUploading(self, uploading):
        if uploading == 0:
            self.uploading_label.setText(f"UPLOADING")
            self.uploading_label.setStyleSheet("color: gray;")
        else:
            self.uploading_label.setText(f"UPLOADING [{uploading:02.0f}]")
            self.uploading_label.setStyleSheet("color: green;")

        self.uploading = uploading
        self.setBusyIndicator()

    @Slot()
    def setResync(self, resync):
        if resync:
            self.resync_label.setText(f"RESYNC")
            self.resync_label.setStyleSheet("color: green;")
        else:
            self.resync_label.setText(f"RESYNC")
            self.resync_label.setStyleSheet("color: gray;")

        self.resync = resync
        self.setBusyIndicator()

    @Slot()
    def setConnected(self, connected):
        if connected:
            self.gnx_connected_label.setStyleSheet("color: green;")
        else:
            self.gnx_connected_label.setStyleSheet("color: red;")
        self.connected = connected

    @Slot()
    def setMIDIChannel(self, channel):
        self.midi_channel_label.setText(f"MIDI Channel: {channel:02.0f}")

    @Slot()
    def patchNameChanged(self, name, bank, patch):
        banks = {0: "FACTORY", 1: "USER"}
        self.patch_label.setText(f"Current Patch: {name} [{banks[bank]}:{(patch + 1):02.0f}]")
