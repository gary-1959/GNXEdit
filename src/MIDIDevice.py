# MIDIDevice.py
#
# GNXEdit MIDI Device Base Class
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

class MIDIDevice:
    name = ""
    mnfr_code = []
    device_id = []

    def __init__(self, name = "Unknown MIDI Device", mnfr_code = [], device_id = []):
        self.name = name
        if mnfr_code == None or len(mnfr_code) == 0:
            raise Exception("No manufacturer code specified")
        else:
            self.mnfr_code = mnfr_code.copy()

        if device_id == None or len(device_id) == 0:
            raise Exception("No devie id specified")
        else:
            self.device_id = device_id.copy()

    def register(self, handler = None):

        if handler == None:
            raise Exception("No MIDI control class specified")
        
        if type(handler).__name__ != "MIDIControl":
            raise Exception("Handler must be MIDIControl class")
        
        handler.register_input_target(self.input_handler)

    def input_handler(self, message):
        print(self.name, message)




