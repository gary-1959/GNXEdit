# MIDIControl.py
#
# GNX Edit MIDI Handler
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

import rtmidi
import settings

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, QObject

class MIDIControl:

    port_in = None
    port_out = None
    midi_input = None
    midi_output = None
    registered_input_targets = None
    registered_ports_open_targets = None
    registered_ports_closed_targets = None

    def __init__(self, window):
        self.window = window
        self.registered_input_targets = []
        self.registered_ports_open_targets = []
        self.registered_ports_closed_targets = []

        self.port_in = rtmidi.MidiIn()
        self.port_in.ignore_types(sysex = False, timing = True, active_sense = True)
        self.port_out = rtmidi.MidiOut()

        innames = self.port_in.get_ports()
        outnames = self.port_out.get_ports()

        # check midi input is valid
        p = 0
        valid = False
        mp = settings.GNXEDIT_CONFIG["midi"]["input"]
        if mp["index"] != None and mp["name"] != None:
            for  n in innames:
                if mp["index"] == p and mp["name"] == n:
                    valid = True
                    break

        if not valid:       # look for USB input
            p = 0
            for  n in innames:
                if n.startswith("USB"):
                    settings.GNXEDIT_CONFIG["midi"]["input"] = {"index": p, "name": n}
                    valid = True
                    break
                p += 1

        if not valid:
            mp = {"index": None, "name": None}

        # check midi output is valid
        p = 0
        valid = False
        mp = settings.GNXEDIT_CONFIG["midi"]["output"]
        if mp["index"] != None and mp["name"] != None:
            for  n in outnames:
                if mp["index"] == p and mp["name"] == n:
                    valid = True
                    break

        if not valid:       # look for USB output
            p = 0
            for  n in outnames:
                if n.startswith("USB"):
                    settings.GNXEDIT_CONFIG["midi"]["output"] = {"index": p, "name": n}
                    valid = True
                    break
                p += 1

        if not valid:
            mp = {"index": None, "name": None}


        settings.save_settings()

    # creates and compares checksum
    def sysex_checksum(self, msg):
        cx = 0
        i = 1
        while i < len(msg) - 2:
            cx = cx ^ msg[i]
            i += 1

        return cx, (cx == msg[i])

    # close all ports
    def close_ports(self):
        # close ports if open
        if self.port_in != None:
            if self.port_in.is_port_open():
                self.port_in.close_port()
                del self.port_in

        if self.port_out != None:
            if self.port_out.is_port_open():
                self.port_out.close_port()
                del self.port_out

        for t in self.registered_ports_closed_targets:
            result = t()

    # open ports according to prefixes in settings
    def open_ports(self):
        self.close_ports()

        if self.port_in == None:
            self.port_in = rtmidi.MidiIn()
            self.port_in.ignore_types(sysex = False, timing = True, active_sense = True)

        if self.port_out == None:   
            self.port_out = rtmidi.MidiOut()

        if self.port_in != None and settings.GNXEDIT_CONFIG["midi"]["input"]["index"] != None:
            self.port_in.open_port(settings.GNXEDIT_CONFIG["midi"]["input"]["index"])
            self.port_in.set_callback(self.input_callback)

        if self.port_out != None and settings.GNXEDIT_CONFIG["midi"]["output"]["index"] != None:
            self.port_out.open_port(settings.GNXEDIT_CONFIG["midi"]["output"]["index"])
        
        if self.port_in == None or not self.port_in.is_port_open():
            raise Exception("Unable to open MIDI input port")
        if self.port_out == None or not self.port_out.is_port_open():
            raise Exception("Unable to open MIDI output port")
        
        for t in self.registered_ports_open_targets:
            result = t()
        
    def register_input_target(self, target = None, **kwargs):
        if target != None:
            if target not in self.registered_input_targets:
                self.registered_input_targets.append(target)
        else:
            raise Exception("Target not specified")

    def deregister_input_target(self, target = None, **kwargs):
        if target != None:
            if target in self.registered_input_targets:
                self.registered_input_targets.remove(target)
        else:
            raise Exception("Target not specified")        
            
    def register_ports_open(self, target = None, **kwargs):
        if target != None:
            if target not in self.registered_ports_open_targets:
                self.registered_ports_open_targets.append(target)
        else:
            raise Exception("Target not specified") 
            
    def register_ports_closed(self, target = None, **kwargs):
        if target != None:
            if target not in self.registered_ports_closed_targets:
                self.registered_ports_closed_targets.append(target)
        else:
            raise Exception("Target not specified") 

    def input_callback(self, event, data = None):
        message, deltatime = event
        # print("Received", message)
        # call all registered targets to receive input events
        # check for sysex
        if message[0] == 0xF0:
            cx, ok = self.sysex_checksum(message)
            if ok:
                for t in self.registered_input_targets:
                    result = t(message)
            else:
                #raise Exception("System Exclusive checksum error")
                print(f"System Exclusive checksum error: received {message[-2]:02X} expected {cx:02X}")
            
        else:
            print("MIDI message: ", message)
            for t in self.registered_input_targets:
                result = t(message)
            pass    # process other messages (e.g. patch change)

    def send_message(self, msg):
        if self.port_out != None:
            if self.port_out.is_port_open():
                # print("Sending", msg)
                self.port_out.send_message(msg)
               
            else:
                raise Exception("MIDI output port not open for sending message")
        else:
            raise Exception("MIDI output port not open")

    def openMIDIDialog(self):
            ui_file_name = "src/ui/mididialog.ui"
            ui_file = QFile(ui_file_name)
            if not ui_file.open(QIODevice.ReadOnly):
                print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
                return

            loader = QUiLoader()
            self.midi_dialog = loader.load(ui_file)

            ui_file.close()
            inputCB = self.midi_dialog.findChild(QComboBox, "inputComboBox")
            innames = self.port_in.get_ports()
            p = 0
            mp = settings.GNXEDIT_CONFIG["midi"]["input"]
            for  n in innames:
                inputCB.addItem(n, p)                
                if mp["index"] != None and mp["name"] != None:
                    if mp["index"] == p and mp["name"] == n:
                        inputCB.setCurrentIndex(p)
                p += 1

            outputCB = self.midi_dialog.findChild(QComboBox, "outputComboBox")
            outnames = self.port_out.get_ports()
            p = 0
            mp = settings.GNXEDIT_CONFIG["midi"]["output"]
            for  n in outnames:
                outputCB.addItem(n, p)                
                if mp["index"] != None and mp["name"] != None:
                    if mp["index"] == p and mp["name"] == n:
                        outputCB.setCurrentIndex(p)
                p += 1

            curChan = self.midi_dialog.findChild(QLabel, "currentChannel")
            curChan.setText(str(settings.GNXEDIT_CONFIG["midi"]["channel"] + 1))

            lockCB = self.midi_dialog.findChild(QComboBox, "lockChannel")
            p = 0
            l = (settings.GNXEDIT_CONFIG["midi"]["lockchannel"] + 1) if settings.GNXEDIT_CONFIG["midi"]["lockchannel"] != None else 0
            for n in ["None"] + [str(x) for x in range(1, 17)]:
                lockCB.addItem(n, p)
                if l == p:
                    lockCB.setCurrentIndex(p)
                p += 1

            self.midi_dialog.accepted.connect(self.midi_dialog_accepted)
            self.midi_dialog.rejected.connect(self.midi_dialog_rejected)
            self.midi_dialog.setParent(self.window, Qt.Dialog)
            self.midi_dialog.show()

    def midi_dialog_accepted(self):
        self.close_ports() 
        inputCB = self.midi_dialog.findChild(QComboBox, "inputComboBox")
        input = inputCB.itemData(inputCB.currentIndex())
        name = inputCB.itemText(inputCB.currentIndex())
        if input == -1:
            settings.GNXEDIT_CONFIG["midi"]["input"] = {"index": None, "name": None}
        else:
            settings.GNXEDIT_CONFIG["midi"]["input"] = {"index": input, "name": name}

        outputCB = self.midi_dialog.findChild(QComboBox, "outputComboBox")
        output = outputCB.itemData(outputCB.currentIndex())
        name = outputCB.itemText(outputCB.currentIndex())
        if output == -1:
            settings.GNXEDIT_CONFIG["midi"]["output"] = {"index": None, "name": None}
        else:
            settings.GNXEDIT_CONFIG["midi"]["output"] = {"index": output, "name": name}


        lockCB = self.midi_dialog.findChild(QComboBox, "lockChannel")
        lockchannel = lockCB.itemData(lockCB.currentIndex()) - 1
        if lockchannel == -1:
            lockchannel = None

        settings.GNXEDIT_CONFIG["midi"]["lockchannel"] = lockchannel

        settings.save_settings()

        self.open_ports()
        pass

    def midi_dialog_rejected(self):
        pass

