# GNX1.py
#
# GNX Edit MIDI Handler for Digitech GNX1
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

from threading import Timer
import time
import os
import settings
from exceptions import GNXError

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QMessageBox, QComboBox, QLineEdit
from PySide6.QtCore import Qt, QFile, QIODevice, QCoreApplication, QDir, Slot, Signal, QObject

from customwidgets.styledial import StyleDial
from customwidgets.ampface import AmpFace
from customwidgets.cabface import CabFace

from customwidgets.factory import factory_pickup_names
from customwidgets.factory import factory_wah_types
from customwidgets.factory import factory_onoff
from customwidgets.factory import factory_compressor_attack
from customwidgets.factory import factory_compressor_ratio
from customwidgets.factory import factory_whammy_shift
from customwidgets.factory import factory_ips_shift
from customwidgets.factory import factory_ips_scale
from customwidgets.factory import factory_ips_key
from customwidgets.factory import factory_waveforms
from customwidgets.factory import factory_expression_assignments

from customwidgets.utils import get_expression_assignment_index
from customwidgets.utils import getnum, skip_bytes, compile_number, pack_data, build_sysex, compare_array
                          
class GNX1(QObject):

    gnxAlert = Signal(GNXError)
    gnxPatchNamesUpdated = Signal(int, list)

    midi_watchdog = None
    midi_watchdog_time = 1  # time between watchdog timeouts
    midi_watchdog_bite_count = 0    # count timeouts before biting
    midi_watchdog_bite_count_limit = 5 # number of timeouts before biting

    resyncing = False   # not resyncing
    uploading = 0       # not uploading
    midicontrol = None
    mnfr_id = [0x00, 0x00, 0x10]
    device_id = 0x56

    midi_channel_offset = 4     # offset in received message to MIDI channel
    device_connected = False
    current_patch_name = None
    current_patch_number = None
    current_patch_bank = None
    user_patch_names = []

    device_pickup = None
    device_wah = None
    device_compressor = None
    device_whammy = None
    device_warp = None
    device_green_amp = None
    device_red_amp = None
    device_green_cab = None
    device_red_amp = None
    device_green_cab = None
    device_red_cab = None
    device_gate = None
    device_mod = None
    device_delay = None
    device_reverb = None
    device_expression = None
    device_lfo = None

    # for saving to library
    code24data = None
    code2Adata = None
    code26data = None
    code28data = None

    last_extra = None
    lastbytes = None

    class watchdog(Exception):
        def __init__(self, timeout = None, userHandler = None):  # timeout in seconds
            self.handler = userHandler if userHandler is not None else self.defaultHandler
            self.timer = None
            if timeout == None:
                self.timeout = 5
            else:
                self.timeout = timeout

        def start(self):
            if self.timer!= None:
                self.timer.cancel()
            self.timer = Timer(self.timeout, self.handler)
            self.timer.daemon = True
            self.timer.start()
            #print("Watchdog started")

        def reset(self):
            if self.timer!= None:
                self.timer.cancel()
            self.timer = Timer(self.timeout, self.handler)
            self.timer.start()
            #print("Watchdog reset")

        def stop(self):
            if self.timer!= None:
                self.timer.cancel()

            #print("Watchdog stopped")

        def defaultHandler(self):
            raise self

    class gnx1_pickup:

        def __init__(self, parent, ui_device):
            self.parent = parent
            self.ui_device = ui_device
            self.ui_device.pickupChanged.connect(self.pickup_changed)

        # from ui device
        def pickup_changed(self, parameter, value):
            self.parent.send_parameter_change(section = 1, parameter = parameter, value = value)

        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():
                match k:
                    case "type":
                        if arg not in factory_pickup_names.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Pickup type not recognised ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setPickup(type = arg)

        # extract pickup value from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked) # may be number of values
            n, type = getnum(n, unpacked)
            self.set_values(type = type)
            
            #print(f"Pickup: Type: {type}")
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_wah:

        def __init__(self, parent, ui_device):
            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.wahChanged.connect(self.wah_changed)
            self.ui_device.pot_min.valueChanged.connect(self.pot_min_changed)
            self.ui_device.pot_max.valueChanged.connect(self.pot_max_changed)
            self.ui_device.pot_pedal.valueChanged.connect(self.pot_pedal_changed)

        # from ui_device
        def wah_changed(self, parameter, value):
            self.parent.send_parameter_change(section = 2, parameter = parameter, value = value)

        def pot_min_changed(self, value):
            self.parent.send_parameter_change(section = 2, parameter = 0x02, value = value)

        def pot_max_changed(self, value):
            self.parent.send_parameter_change(section = 2, parameter = 0x03, value = value)

        def pot_pedal_changed(self, value):
            self.parent.send_parameter_change(section = 2, parameter = 0x04, value = value)

        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():
                match k:
                    case "type":
                        if arg not in factory_wah_types.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Wah type ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWah(type = arg)

                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Wah on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWah(on = arg)

                    case "min":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Wah minimum value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_min.setValue(arg)

                    case "max":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Wah maximum value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)        
                        else:
                            setattr(self, k, arg)
                            self.ui_device.pot_max.setValue(arg)

                    case "pedal":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Pedal maximum value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_pedal.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked) # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)
            n, min = getnum(n, unpacked)
            n, max = getnum(n, unpacked)
            n, pedal = getnum(n, unpacked)

            self.set_values(type = type, on = on, min = min, max = max, pedal = pedal)
            
            #print("WAH: {0}, Type: {1}, Min: {2}, Max: {3}, Pedal:{4}".format(factory_onoff[on], factory_wah_types[type], min, max, pedal))
            return n

        # individual parameter change from GNX1
        parameter_names = ["type", "on", "min", "max", "pedal"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_compressor(QObject):

        compressorPotChanged = Signal(int, int, dict, str)    # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()
            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.compressorChanged.connect(self.compressor_changed)
            self.ui_device.compressorPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_ratio.valueChanged.connect(self.pot_ratio_changed)
            self.ui_device.pot_threshold.valueChanged.connect(self.pot_threshold_changed)
            self.ui_device.pot_gain.valueChanged.connect(self.pot_gain_changed)

        def sendExpPots(self, parameter, pot):     # for expression from ui_device
            name = "Compressor"
            match parameter:
                case 0x02:
                    name = "Compressor Attack"
                case 0x03:
                    name = "Compressor Ratio"
                case 0x04:
                    name = "Compressor Threshold"
                case 0x05:
                    name = "Compressor Gain"

            self.compressorPotChanged.emit(0x03, parameter, pot, name)

        # from ui_device
        def compressor_changed(self, parameter, value):
            self.parent.send_parameter_change(section = 3, parameter = parameter, value = value)

        def pot_ratio_changed(self, value):
            self.parent.send_parameter_change(section = 3, parameter = 0x03, value = value)

        def pot_threshold_changed(self, value):
            self.parent.send_parameter_change(section = 3, parameter = 0x04, value = value)

        def pot_gain_changed(self, value):
            self.parent.send_parameter_change(section = 3, parameter = 0x05, value = value)

        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Compressor on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setCompressor(on = arg)
                            
                    case "attack":
                        if arg not in factory_compressor_attack.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Compressor Attack value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setCompressor(attack = arg)

                    case "ratio":
                        if arg not in factory_compressor_ratio.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Compressor Ratio value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_ratio.setValue(arg)
                            self.ui_device.updateLabel1()

                    case "threshold":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Compressor Threshold value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_threshold.setValue(arg)

                    case "gain":
                        if arg < 0 or arg > 20:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Compressor Gain value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_gain.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)       # always zero
            n, on = getnum(n, unpacked)
            n, attack = getnum(n, unpacked)
            n, ratio = getnum(n, unpacked)
            n, threshold = getnum(n, unpacked)
            n, gain = getnum(n, unpacked)

            self.set_values(on = on, attack = attack, ratio = ratio, threshold = threshold, gain = gain)
            
            #print("COMPRESSOR: {0}, Attack: {1}, Ratio: {2}, Threshold: {3}, Gain:{4}".format(
            #      factory_onoff[on], factory_compressor_attack[attack], factory_compressor_ratio[ratio],
            #        threshold, gain))
            
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "attack", "ratio", "threshold", "gain"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_whammy(QObject):

        whammyPotChanged = Signal(int, int, dict, str) # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()
            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.whammyChanged.connect(self.whammy_changed)
            self.ui_device.whammyPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_1.valueChanged.connect(self.pot_1_changed)
            self.ui_device.pot_2.valueChanged.connect(self.pot_2_changed)
            self.ui_device.pot_3.valueChanged.connect(self.pot_3_changed)
            self.ui_device.pot_4.valueChanged.connect(self.pot_4_changed)

            self.type = 0

        def sendExpPots(self, parameter, pot, type): # for expression from ui_device
            name = None
            match type:
                case 0: # Whammy
                    name = "Whammy"
                    match parameter:
                        case 0x02:
                            name = "Whammy Shift Amount"
                        case 0x03:
                            name = "Whammy Pedal"
                        case 0x04:
                            name = "Whammy Mix"
                        case 0x05:
                            name = None

                case 1: # IPS
                    name = "IPS"
                    match parameter:
                        case 0x02:
                            name = "IPS Shift Amount"
                        case 0x03:
                            name = "IPS Scale"
                        case 0x04:
                            name = "IPS Key"
                        case 0x05:
                            name = "IPS Level"

                case 2: # Detune
                    name = "Detune"
                    match parameter:
                        case 0x02:
                            name = "Whammy Detune Amount"
                        case 0x03:
                            name = "Whammy Detune Level"
                        case 0x04:
                            name = None
                        case 0x05:
                            name = None

                case 3: # Pitch
                    name = "Pitch"
                    match parameter:
                        case 0x02:
                            name = "Whammy Pitch Amount"
                        case 0x03:
                            name = "Whammy Pitch Level"
                        case 0x04:
                            name = None
                        case 0x05:
                            name = None

            self.whammyPotChanged.emit(0x04, parameter, pot, name)

        # from ui_device
        def whammy_changed(self, parameter, value):
            if parameter == 0:
                self.type = value
            self.parent.send_parameter_change(section = 4, parameter = parameter, value = value)

        def pot_1_changed(self, value):
            self.parent.send_parameter_change(section = 4, parameter = 0x02, value = value)

        def pot_2_changed(self, value):
            self.parent.send_parameter_change(section = 4, parameter = 0x03, value = value)

        def pot_3_changed(self, value):
            self.parent.send_parameter_change(section = 4, parameter = 0x04, value = value)

        def pot_4_changed(self, value):
            self.parent.send_parameter_change(section = 4, parameter = 0x05, value = value)

        # from GNX 1
        def set_values(self, **kwargs):
            maxlimits = {   # by type
                0: {"param_1": len(factory_whammy_shift) - 1, "param_2": 99, "param_3": 99, "param_4": 99},
                1: {"param_1": len(factory_ips_shift) - 1, "param_2": len(factory_ips_scale) - 1, "param_3": len(factory_ips_key) - 1, "param_4": 99},
                2: {"param_1": 24, "param_2": 99, "param_3": 99, "param_4": 99},
                3: {"param_1": 48, "param_2": 99, "param_3": 99, "param_4": 99}
            }
                         
            for k, arg in kwargs.items():
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy/IPS on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWhammy(on = arg)

                    case "type":
                        if arg < 0 or arg > 3:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy Type value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.type = arg
                            self.ui_device.setWhammy(type = arg)

                    case "param_1":
                        if arg < 0 or arg > maxlimits[self.type]["param_1"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy Param 1 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_1.setValue(arg)
                            self.ui_device.updateLabel1()

                    case "param_2":
                        if arg < 0 or arg > maxlimits[self.type]["param_2"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy Param 2 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_2.setValue(arg)
                            self.ui_device.updateLabel2()

                    case "param_3":
                        if arg < 0 or arg > maxlimits[self.type]["param_3"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy Param 3 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_3.setValue(arg)
                            self.ui_device.updateLabel3()

                    case "param_4":
                        if arg < 0 or arg > maxlimits[self.type]["param_4"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Whammy Param 4 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_4.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)

            self.type = type
            match type:             # variable number of parameters depending on type
                case 0: # whammy
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    n, param_3 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3)
                    #print("WHAMMY: {0}, Shift {1}, Pedal {2}, Mix {3}".format(
                    #    factory_onoff[on], factory_whammy_shift[param_1], param_2, param_3))

                case 1: # IPS
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    n, param_3 = getnum(n, unpacked)
                    n, param_4 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3, param_4 = param_4)
                    #print("IPS: {0}, Shift {1}, Scale {2}, Key {3}, Level {4}".format(
                    #    factory_onoff[on], factory_ips_shift[param_1], factory_ips_scale[param_2],
                    #      factory_ips_key[param_3], param_4))

                case 2: # detune
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2)
                    #print("DETUNE: {0}, Shift {1}, Level {2}".format(
                    #    factory_onoff[on], param_1, param_2))

                case 3: # pitch
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2)
                    #print("PITCH: {0}, Shift {1}, Level {2}".format(
                    #    factory_onoff[on], param_1, param_2))
                case _:
                    e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Unrecognised Whammy/IPS type {type}", buttons = QMessageBox.Ok)
                    self.parent.gnxAlert.emit(e)

            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "param_1", "param_2", "param_3", "param_4"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})
    
    class gnx1_warp(QObject):

        warpPotChanged = Signal(int, int, dict, str)    # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()
            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.warpChanged.connect(self.warp_changed)
            self.ui_device.warpPotChanged.connect(self.sendExpPots)

        def sendExpPots(self, parameter, pot):
            name = "Warp"
            match parameter:
                case 0x01:
                    name = "Amp Channel"
                case 0x02:
                    name = "Amp Warp"
                case 0x03:
                    name = "Cab Warp"
                case 0x04:
                    name = "Warp"

            self.warpPotChanged.emit(0x05, parameter, pot, name)

        # from ui_device
        def warp_changed(self, parameter, value):
            self.parent.send_parameter_change(section = 5, parameter = parameter, value = value)

        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():
                match k:
                    case "type":
                        if arg < 0 or arg > 0:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp Type ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWarpFactor(type = arg)

                    case "amp_select":
                        if arg < 0 or arg > 2:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp Select type ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)    
                        else:
                            self.ui_device.setWarpFactor(amp_select = arg)

                    case "amp_warp":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp Warp ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWarpFactor(amp_warp = arg)

                    case "cab_warp":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Cab Warp ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setWarpFactor(cab_warp = arg)         

                    case "warpD":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Warp Param D ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:  
                            self.ui_device.setWarpFactor(warpD = arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked) # may be number of values
            n, type = getnum(n, unpacked) # always zero
            n, amp_select = getnum(n, unpacked)
            n, amp_warp = getnum(n, unpacked)
            n, cab_warp = getnum(n, unpacked)
            n, warpD = getnum(n, unpacked)
            
            self.set_values(type = type, amp_select = amp_select, amp_warp = amp_warp, cab_warp = cab_warp, warpD = warpD)
            
            #print(f"WARP: Amp Select: {amp_select}, Amp Warp: {amp_warp}, Cab Warp: {cab_warp}, D: {warpD}")
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "amp_select", "amp_warp", "cab_warp", "warpD"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})
        
    class gnx1_amp(QObject):

        ampPotChanged = Signal(int, int, dict, str)     # section, parameter, pot, name

        def __init__(self, parent, ui_device, section):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device      # ampface
            self.section = section          # parameter section

            self.ui_device.ampStyleChanged.connect(self.amp_style_changed)
            self.ui_device.ampPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_gain.valueChanged.connect(self.pot_gain_changed)
            self.ui_device.pot_bass_freq.valueChanged.connect(self.pot_bass_freq_changed)
            self.ui_device.pot_bass_level.valueChanged.connect(self.pot_bass_level_changed)
            self.ui_device.pot_mid_freq.valueChanged.connect(self.pot_mid_freq_changed)
            self.ui_device.pot_mid_level.valueChanged.connect(self.pot_mid_level_changed)
            self.ui_device.pot_treble_freq.valueChanged.connect(self.pot_treble_freq_changed)
            self.ui_device.pot_treble_level.valueChanged.connect(self.pot_treble_level_changed)
            self.ui_device.pot_level.valueChanged.connect(self.pot_level_changed)

        def sendExpPots(self, parameter, pot):      # for expression from ui_device
            name = "Amp"
            color = "Green" if self.section == 0x06 else "Red"
            match parameter:
                case 0x01:
                    name = f"{color} Amp Gain"
                case 0x08:
                    name = f"{color} Amp Level"

            self.ampPotChanged.emit(self.section, parameter, pot, name)

        # from GNX1
        def set_values(self, **kwargs):

            for k, arg in kwargs.items():

                if arg == None:
                    continue

                match k:
                    case "name":
                        #print("Set amp style by name deprecated")
                        pass    # deprecated
                        '''
                        if isinstance(arg, int):
                            if arg not in factory_amp_names.keys():
                                arg = 0
                            arg = .factory_amp_names[arg]
                            
                        if arg.upper() not in factory_amp_names.values():
                            arg = "USER"
                        
                        arg = arg.strip()
                        setattr(self, k, arg.lower())
                        self.ui_device.setAmpStyle(arg.lower())
                        '''

                    case "type":
                        if arg not in self.ui_device.AMP_STYLES.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Unrecognised amp type {arg}", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setAmpStyle(arg)

                    case "gain":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp gain value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_gain.setValue(arg)
                        
                    case "bass_freq":
                        if arg < 0 or arg > 250:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp bass frequency value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_bass_freq.setValue(arg)

                    case "bass_level":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp bass level value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_bass_level.setValue(arg)

                    case "mid_freq":
                        if arg < 0 or arg > 4700:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp mid frequency value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_mid_freq.setValue(arg)

                    case "mid_level":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp mid level value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_mid_level.setValue(arg)

                    case "treble_freq":
                        if arg < 0 or arg > 7500:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp treble frequency value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_treble_freq.setValue(arg)

                    case "treble_level":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp treble level value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_treble_level.setValue(arg)

                    case "level":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Amp level value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_level.setValue(arg)

                    case "_":
                        e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Unrecognised amp parameter ({arg})", buttons = QMessageBox.Ok)
                        self.parent.gnxAlert.emit(e)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked) # may be number of values
            n, type = getnum(n, unpacked)
            n, gain = getnum(n, unpacked)
            n, bass_freq = getnum(n, unpacked)
            n, bass_level = getnum(n, unpacked)
            n, mid_freq = getnum(n, unpacked)
            n, mid_level = getnum(n, unpacked)
            n, treble_freq = getnum(n, unpacked)
            n, treble_level = getnum(n, unpacked)
            n, level = getnum(n, unpacked)


            self.set_values(type = type, gain = gain, bass_freq = bass_freq, bass_level = bass_level, mid_freq = mid_freq, mid_level = mid_level,
                            treble_freq = treble_freq, treble_level = treble_level, level = level )
            
            #print("AMP: Type: {0}, Gain: {1}, Bass Freq: {2}, Bass level: {3}, Mid Freq: {4}, Mid Level: {5}, Treble Freq: {6}, Treble Level: {7}, Level: {8}".format(
            #    type, gain, bass_freq, bass_level, mid_freq, mid_level, treble_freq, treble_level, level))
            return n

        # extract amp values from data string
        # get values from code 2A response
        def get_values2A(self, unpacked):
            n = 7
            name = ""
            while unpacked[n] != 0:
                name += chr(unpacked[n])
                n += 1

            n = 574 + len(name)   # hopefully this lines up

            bass_freq = unpacked[n] * 256 + unpacked[n + 1]
            n += 2
            mid_freq = unpacked[n] * 256 + unpacked[n + 1]
            n += 2
            treble_freq = unpacked[n] * 256 + unpacked[n + 1]
            n += 2

            bass_level = unpacked[n]
            n += 1
            mid_level = unpacked[n]
            n += 1
            treble_level = unpacked[n]
            n += 1
            gain = unpacked[n]
            n += 1
            level = unpacked[n]
            n += 1

            self.set_values(name = name.lower(), gain = gain, level = level, bass_freq = bass_freq, bass_level = bass_level,
                            mid_freq = mid_freq, mid_level = mid_level, treble_freq = treble_freq, treble_level = treble_level)

        # from ui_device
        def amp_style_changed(self, value):
            # GNX1 responds with amp settings
            #print(f"Amp Style {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x00, value = value)

        def pot_gain_changed(self, value):
            #print(f"Pot Gain {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x01, value = value)

        def pot_bass_freq_changed(self, value):
            #print(f"Pot Bass Freq {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x02, value = value)

        def pot_bass_level_changed(self, value):
            #print(f"Pot Bass Level {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x03, value = value)

        def pot_mid_freq_changed(self, value):
            #print(f"Pot Mid Freq {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x04, value = value)

        def pot_mid_level_changed(self, value):
            #print(f"Pot Mid Level {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x05, value = value)

        def pot_treble_freq_changed(self, value):
            #print(f"Pot Treble Freq {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x06, value = value)

        def pot_treble_level_changed(self, value):
            #print(f"Pot Treble Level {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x07, value = value)

        def pot_level_changed(self, value):
            #print(f"Pot Level {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x08, value = value)

        # individual parameter change from GNX1
        parameter_names = ["type", "gain", "bass_freq", "bass_level", "mid_greq", "mid_level", "treble_freq", "treble_level", "level"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})
            
    class gnx1_cab:

        def __init__(self, parent, ui_device, section):
            self.parent = parent
            self.ui_device = ui_device
            self.section = section          # parameter section

            self.ui_device.cabStyleChanged.connect(self.cab_style_changed)
            self.ui_device.pot_tuning.valueChanged.connect(self.pot_tuning_changed)
       
        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():

                if arg == None:
                    continue

                match k:
                    case "type":
                        if arg not in self.ui_device.CAB_STYLES.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Unrecognised cab type {arg}", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setCabStyle(arg)

                    case "tuning":
                        if arg < 0 or arg > 48:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Cabinet tuning value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_tuning.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked) # may be number of values
            n, type = getnum(n, unpacked)
            n, tuning = getnum(n, unpacked)

            self.set_values(type = type, tuning = tuning)
            
            #print("CAB: Type: {0}, Tuning: {1}".format(type, tuning))
            return n

        # get values from code 2A response
        def get_values2A(self, unpacked):
            n = 7
            name = ""
            while unpacked[n] != 0:
                name += chr(unpacked[n])
                n += 1

            # cab tuning?

            self.set_values(name = name)

        # from ui_device
        def cab_style_changed(self, value):
            # GNX1 responds with cab settings
            #print(f"Cab Style {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x00, value = value)

        def pot_tuning_changed(self, value):
            #print(f"Tuing {value}")
            self.parent.send_parameter_change(section = self.section, parameter = 0x01, value = value)

        # individual parameter change from GNX1
        parameter_names = ["type", "tuning"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_gate(QObject):

        gatePotChanged = Signal(int, int, dict, str) # section, parameter, pot, name
        
        def __init__(self, parent, ui_device):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.gateChanged.connect(self.gate_changed)
            self.ui_device.gatePotChanged.connect(self.sendExpPots)
            self.ui_device.pot_1.valueChanged.connect(self.pot_1_changed)
            self.ui_device.pot_2.valueChanged.connect(self.pot_2_changed)
            self.ui_device.pot_3.valueChanged.connect(self.pot_3_changed)

            self.type = 0

        def sendExpPots(self, parameter, pot, type): # for expression from ui_device
            name = None
            match type:
                case 0: # silencer
                    match parameter:
                        case 0x02:
                            name = "Gate Threshold"
                        case 0x03:
                            name = "Gate Attack"
                        case 0x04:
                            name = None

                case 1: # pluck
                    match parameter:
                        case 0x02:
                            name = "Gate Threshold"
                        case 0x03:
                            name = "Gate Attack"
                        case 0x04:
                            name = "Gate Sensitivity"

            self.gatePotChanged.emit(0x0A, parameter, pot, name)

        # from ui_device
        def gate_changed(self, parameter, value):
            if parameter == 0:
                self.type = value
            self.parent.send_parameter_change(section = 10, parameter = parameter, value = value)

        def pot_1_changed(self, value):
            self.parent.send_parameter_change(section = 10, parameter = 0x02, value = value)

        def pot_2_changed(self, value):
            self.parent.send_parameter_change(section = 10, parameter = 0x03, value = value)

        def pot_3_changed(self, value):
            self.parent.send_parameter_change(section = 10, parameter = 0x04, value = value)

        # from GNX1
        def set_values(self, **kwargs):
                         
            for k, arg in kwargs.items():
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Gate on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setGate(on = arg)

                    case "type":
                        if arg < 0 or arg > 1:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Gate Type value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.type = arg
                            self.ui_device.setGate(type = arg)

                    case "param_1":
                        if arg < 0 or arg > 40:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Gate Threshold value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_1.setValue(arg)

                    case "param_2":
                        if arg < 0 or arg > 9:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Gate Attack value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_2.setValue(arg)

                    case "param_3":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Gate Sensitivity value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_3.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)

            self.type = type
            match type:             # variable number of parameters depending on type
                case 0: # silencer
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2)
                    #print("GATE: {0}, Threshold {1}, Attack {2}".format(
                    #    factory_onoff[on], param_1, param_1))

                case 1: # pluck
                    n, param_1 = getnum(n, unpacked)
                    n, param_2 = getnum(n, unpacked)
                    n, param_3 = getnum(n, unpacked)
                    self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3)
                    #print("GATE: {0}, Threshold {1}, Attack {2}, Sensitivity {3}".format(
                    #    factory_onoff[on], param_1, param_2, param_3))
                    
                case _:
                    e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Unrecognised Gate type {type}", buttons = QMessageBox.Ok)
                    self.parent.gnxAlert.emit(e)
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "param_1", "param_2", "param_3"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_mod(QObject):

        modPotChanged = Signal(int, int, dict, str)  # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.modChanged.connect(self.mod_changed)
            self.ui_device.modPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_1.valueChanged.connect(self.pot_1_changed)
            self.ui_device.pot_2.valueChanged.connect(self.pot_2_changed)
            self.ui_device.pot_3.valueChanged.connect(self.pot_3_changed)
            self.ui_device.pot_4.valueChanged.connect(self.pot_4_changed)
            self.ui_device.pot_5.valueChanged.connect(self.pot_5_changed)
            self.ui_device.pot_6.valueChanged.connect(self.pot_6_changed)

            self.type = 0

        def sendExpPots(self, parameter, pot, type):

            names = {
                        0: {0x02:"Chorus Speed", 0x03: "Chorus Depth", 0x04: "Chorus Pre Delay", 0x05: None, 0x06: "Chorus Balance", 0x07: "Chorus Mix"},
                        1: {0x02:"Flanger Speed", 0x03: "Flanger Depth", 0x04: "Flanger Regen", 0x05: None, 0x06: "Flanger Balance", 0x07: "Flanger Mix"},
                        2: {0x02:"Phaser Speed", 0x03: "Phaser Depth", 0x04: "Phaser Regen", 0x05: None, 0x06: "Phaser Balance", 0x07: "Phaser Mix"},
                        3: {0x02:"Flanger Speed", 0x03: "Flanger Sensitivity", 0x04: "Flanger LFO Start", 0x05: "Flanger Mix", 0x06: None, 0x07: None},
                        4: {0x02:"Phaser Speed", 0x03: "Phaser Sensitivity", 0x04: "Phaser LFO Start", 0x05: "Phaser Mix", 0x06: None, 0x07: None},
                        5: {0x02:"Tremelo Speed", 0x03: "Tremelo Depth", 0x04: None, 0x05: None, 0x06: None, 0x07: None},
                        6: {0x02:"Panner Speed", 0x03: "Panner Depth", 0x04: None, 0x05: None, 0x06: None, 0x07: None},
                        7: {0x02:"Vibrato Speed", 0x03: "Vibrato Depth", 0x04: None, 0x05: None, 0x06: None, 0x07: None},
                        8: {0x02:"Rotary Speed", 0x03: "Rotary Depth", 0x04: "Rotary Doppler", 0x05: "Rotary X-Over", 0x06: "Rotary Balance", 0x07: "Rotary Mix"},
                        9: {0x02:"Auto Ya Speed", 0x03: "Auto Ya Depth", 0x04: "Auto Ya Range", 0x05: "Auto Ya Balance", 0x06: "Auto Ya Mix", 0x07: None},
                        10: {0x02:"Ya Ya Pedal", 0x03: "Ya Ya Depth", 0x04: "Ya Ya Range", 0x05: "Ya Ya Balance", 0x06: "Ya Ya Mix", 0x07: None},
                        11: {0x02:"Synth Attack", 0x03: "Synth Release", 0x04: "Synth Vox", 0x05: "Synth Balance", 0x06: "Synth Sensitivity", 0x07: None},
                        12: {0x02:"Envelope Sensitivity", 0x03: "Envelope Range", 0x04: "Envelope Balance", 0x05: "Envelope Mix", 0x06: None, 0x07: None},
                        13: {0x02:"Detune Amount", 0x03: "Detune Balance", 0x04: "Detune Mix", 0x05: None, 0x06: None, 0x07: None},
                        14: {0x02:"Pitch Amount", 0x03: "Pitch Balance", 0x04: "Picth Level", 0x05: None, 0x06: None, 0x07: None}
            }

            self.modPotChanged.emit(0x0B, parameter, pot, names[type][parameter])

        # from ui_device
        def mod_changed(self, parameter, value):
            if parameter == 0:
                self.type = value
            self.parent.send_parameter_change(section = 11, parameter = parameter, value = value)

        def pot_1_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x02, value = value)

        def pot_2_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x03, value = value)

        def pot_3_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x04, value = value)

        def pot_4_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x05, value = value)

        def pot_5_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x06, value = value)

        def pot_6_changed(self, value):
            self.parent.send_parameter_change(section = 11, parameter = 0x07, value = value)

        # from GNX1
        def set_values(self, **kwargs):
            maxlimits = {   # by type
                0: {"param_1": 98, "param_2": 98, "param_3": 19, "param_4": 2, "param_5": 198, "param_6": 99},
                1: {"param_1": 98, "param_2": 98, "param_3": 99, "param_4": 2, "param_5": 198, "param_6": 99},
                2: {"param_1": 98, "param_2": 98, "param_3": 99, "param_4": 2, "param_5": 198, "param_6": 99},
                3: {"param_1": 98, "param_2": 98, "param_3": 99, "param_4": 99},
                4: {"param_1": 98, "param_2": 98, "param_3": 99, "param_4": 99},
                5: {"param_1": 98, "param_2": 99, "param_3": 2},
                6: {"param_1": 98, "param_2": 99, "param_3": 2},
                7: {"param_1": 98, "param_2": 98, "param_3": 2},
                8: {"param_1": 99, "param_2": 99, "param_3": 99, "param_4": 130, "param_5": 198, "param_6": 99},
                9: {"param_1": 98, "param_2": 98, "param_3": 50, "param_4": 198, "param_5": 99},
                10: {"param_1": 99, "param_2": 98, "param_3": 50, "param_4": 198, "param_5": 99},
                11: {"param_1": 99, "param_2": 100, "param_3": 99, "param_4": 198, "param_5": 99},
                12: {"param_1": 98, "param_2": 98, "param_3": 198, "param_4": 99},
                13: {"param_1": 48, "param_2": 198, "param_3": 99},
                14: {"param_1": 36, "param_2": 198, "param_3": 99},
            }
                         
            for k, arg in kwargs.items():
                if arg == None:
                    continue
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setMod(on = arg)

                    case "type":
                        if arg < 0 or arg > 14:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Type value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.type = arg
                            self.ui_device.setMod(type = arg)

                    case "param_1":
                        if arg < 0 or arg > maxlimits[self.type]["param_1"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 1 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_1.setValue(arg)

                    case "param_2":
                        if arg < 0 or arg > maxlimits[self.type]["param_2"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 2 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_2.setValue(arg)

                    case "param_3":
                        if arg < 0 or arg > maxlimits[self.type]["param_3"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 3 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_3.setValue(arg)

                    case "param_4":
                        if arg < 0 or arg > maxlimits[self.type]["param_4"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 4 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_4.setValue(arg)

                    case "param_5":
                        if arg < 0 or arg > maxlimits[self.type]["param_5"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 5 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_5.setValue(arg)

                    case "param_6":
                        if arg < 0 or arg > maxlimits[self.type]["param_6"]:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Mod Param 6 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_6.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)

            param_1 = param_2 = param_3 = param_4 = param_5 = param_6 = None

            self.type = type
            nparams = [6, 6, 6, 4, 4, 3, 3, 3, 6, 5, 5, 5, 4, 3, 3]
            n, param_1 = getnum(n, unpacked)
            n, param_2 = getnum(n, unpacked)
            n, param_3 = getnum(n, unpacked)
            if nparams[self.type] > 3:
                n, param_4 = getnum(n, unpacked)
            if nparams[self.type] > 4:
                n, param_5 = getnum(n, unpacked)
            if nparams[self.type] > 5:
                n, param_6 = getnum(n, unpacked)
                
            self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3, param4 = param_4, param_5 = param_5, param_6 = param_6)
            #print("MOD: {0}, Param 1 {1}, Param 2 {2}, Param 3 {3}, Param 4 {4}, Param 5 {5}, Param 6 {6}".format(
            #            factory_onoff[on], param_1, param_2, param_3, param_4, param_5, param_6))
               
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "param_1", "param_2", "param_3", "param_4,", "param_5", "param_6"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_delay(QObject):

        delayPotChanged = Signal(int, int, dict, str)  # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.delayChanged.connect(self.delay_changed)
            self.ui_device.delayPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_1.valueChanged.connect(self.pot_1_changed)
            self.ui_device.pot_2.valueChanged.connect(self.pot_2_changed)
            self.ui_device.pot_3.valueChanged.connect(self.pot_3_changed)
            self.ui_device.pot_4.valueChanged.connect(self.pot_4_changed)
            self.ui_device.pot_5.valueChanged.connect(self.pot_5_changed)
            self.ui_device.pot_6.valueChanged.connect(self.pot_6_changed)

            self.type = 0

        def sendExpPots(self, parameter, pot):  # for expression from ui_device
            names = {0x02: "Delay Time", 0x03: "Delay Feedback", 0x04: "Delay Duck Threshold", 0x05: "Delay Duck Attenuation", 0x06: "Delay Balance", 0x07: "Delay Level"}
            self.delayPotChanged.emit(0x0C, parameter, pot, names[parameter])

        # from ui_device
        def delay_changed(self, parameter, value):
            if parameter == 0:
                self.type = value
            self.parent.send_parameter_change(section = 12, parameter = parameter, value = value)

        def pot_1_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x02, value = value)

        def pot_2_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x03, value = value)

        def pot_3_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x04, value = value)

        def pot_4_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x05, value = value)

        def pot_5_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x06, value = value)

        def pot_6_changed(self, value):
            self.parent.send_parameter_change(section = 12, parameter = 0x07, value = value)

        # from GNX1
        def set_values(self, **kwargs):
                         
            for k, arg in kwargs.items():
                if arg == None:
                    continue
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setDelay(on = arg)

                    case "type":
                        if arg < 0 or arg > 3:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Type value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.type = arg
                            self.ui_device.setDelay(type = arg)

                    case "param_1":
                        if arg < 0 or arg > 2000:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 1 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_1.setValue(arg)

                    case "param_2":
                        if arg < 0 or arg > 100:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 2 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_2.setValue(arg)

                    case "param_3":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 3 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_3.setValue(arg)

                    case "param_4":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 4 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_4.setValue(arg)

                    case "param_5":
                        if arg < 0 or arg > 198:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 5 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_5.setValue(arg)

                    case "param_6":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Delay Param 6 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_6.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)

            param_1 = param_2 = param_3 = param_4 = param_5 = param_6 = None

            self.type = type
            n, param_1 = getnum(n, unpacked)
            n, param_2 = getnum(n, unpacked)
            n, param_3 = getnum(n, unpacked)
            n, param_4 = getnum(n, unpacked)
            n, param_5 = getnum(n, unpacked)
            n, param_6 = getnum(n, unpacked)
                
            self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3, param4 = param_4, param_5 = param_5, param_6 = param_6)
            #print("DELAY: {0}, Param 1 {1}, Param 2 {2}, Param 3 {3}, Param 4 {4}, Param 5 {5}, Param 6 {6}".format(
            #            factory_onoff[on], param_1, param_2, param_3, param_4, param_5, param_6))
               
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "param_1", "param_2", "param_3", "param_4,", "param_5", "param_6"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})

    class gnx1_reverb(QObject):

        reverbPotChanged = Signal(int, int, dict, str)  # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()
            
            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.reverbChanged.connect(self.reverb_changed)
            self.ui_device.reverbPotChanged.connect(self.sendExpPots)
            self.ui_device.pot_1.valueChanged.connect(self.pot_1_changed)
            self.ui_device.pot_2.valueChanged.connect(self.pot_2_changed)
            self.ui_device.pot_3.valueChanged.connect(self.pot_3_changed)
            self.ui_device.pot_4.valueChanged.connect(self.pot_4_changed)
            self.ui_device.pot_5.valueChanged.connect(self.pot_5_changed)

            self.type = 0

        def sendExpPots(self, parameter, pot):  # for expression from ui_device
            names = {0x02: "Reverb Pre Delay", 0x03: "Reverb Decay", 0x04: "Reverb Damping", 0x05: "Reverb Balance", 0x06: "Reverb Level"}
            self.reverbPotChanged.emit(0x0D, parameter, pot, names[parameter])

        # from ui_device
        def reverb_changed(self, parameter, value):
            if parameter == 0:
                self.type = value
            self.parent.send_parameter_change(section = 13, parameter = parameter, value = value)

        def pot_1_changed(self, value):
            self.parent.send_parameter_change(section = 13, parameter = 0x02, value = value)

        def pot_2_changed(self, value):
            self.parent.send_parameter_change(section = 13, parameter = 0x03, value = value)

        def pot_3_changed(self, value):
            self.parent.send_parameter_change(section = 13, parameter = 0x04, value = value)

        def pot_4_changed(self, value):
            self.parent.send_parameter_change(section = 13, parameter = 0x05, value = value)

        def pot_5_changed(self, value):
            self.parent.send_parameter_change(section = 13, parameter = 0x06, value = value)

        # from GNX1
        def set_values(self, **kwargs):
                         
            for k, arg in kwargs.items():
                if arg == None:
                    continue
                match k:
                    case "on":
                        if arg not in factory_onoff.keys():
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb on/off ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.setReverb(on = arg)

                    case "type":
                        if arg < 0 or arg > 9:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Type value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.type = arg
                            self.ui_device.setReverb(type = arg)

                    case "param_1":
                        if arg < 0 or arg > 15:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Param 1 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_1.setValue(arg)

                    case "param_2":
                        if arg < 0 or arg > 98:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Param 2 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_2.setValue(arg)

                    case "param_3":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Param 3 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_3.setValue(arg)

                    case "param_4":
                        if arg < 0 or arg > 198:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Param 4 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_4.setValue(arg)

                    case "param_5":
                        if arg < 0 or arg > 99:
                            e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Reverb Param 5 value ({arg})", buttons = QMessageBox.Ok)
                            self.parent.gnxAlert.emit(e)
                        else:
                            self.ui_device.pot_5.setValue(arg)

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            n, nbytes = getnum(n, unpacked)     # may be number of values
            n, type = getnum(n, unpacked)
            n, on = getnum(n, unpacked)

            param_1 = param_2 = param_3 = param_4 = param_5 = None

            self.type = type
            n, param_1 = getnum(n, unpacked)
            n, param_2 = getnum(n, unpacked)
            n, param_3 = getnum(n, unpacked)
            n, param_4 = getnum(n, unpacked)
            n, param_5 = getnum(n, unpacked)
                
            self.set_values(on = on, type = type, param_1 = param_1, param_2 = param_2, param_3 = param_3, param4 = param_4, param_5 = param_5)
            #print("DELAY: {0}, Param 1 {1}, Param 2 {2}, Param 3 {3}, Param 4 {4}, Param 5 {5}".format(
            #            factory_onoff[on], param_1, param_2, param_3, param_4, param_5))
               
            return n
        
        # individual parameter change from GNX1
        parameter_names = ["type", "on", "param_1", "param_2", "param_3", "param_4,", "param_5"]
        def parameter_change(self, parameter, value):
            # parameter is an index
            name = self.parameter_names[parameter]
            self.set_values(**{name: value})
        
    class gnx1_expression(QObject):

        def __init__(self, parent, ui_device):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device
        
            self.ui_device.expChanged.connect(self.parent.sendcode26message)
            for x in range(0, 3):
                for m in ["min", "max"]:
                    self.ui_device.pots[x][m].valueChanged.connect(self.parent.sendcode26message)
                    pass

        # from GNX1
        def set_values(self, **kwargs):
            for k, arg in kwargs.items():

                if arg == None:
                    continue

                match k:
                    case "assignment":
                        for x in range(0, 3):
                            section = arg[x]["section"]
                            parameter = arg[x]["parameter"] if section != 0xFF else 0xFF # make parameter 0xFF id section is 0xFF
                            a = get_expression_assignment_index(section, parameter)
                            if a == None:
                                e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in Expression {x} Pedal Assign (Section {section:02X} Parameter {parameter:02X})", buttons = QMessageBox.Ok)
                                self.parent.gnxAlert.emit(e)
                            else:
                                self.ui_device.setAssignment(x, a)

                    case "params":
                       
                        for x in range(0, 3):
                            self.ui_device.setParameters(x, arg[x])
                            pass

        # extract values from GNX1 data string and return next position
        def get_values(self, n, unpacked):
            assignment = []
            params = []
            for i in range(0, 3):
                assignment.append({"section": unpacked[n], "parameter": unpacked[n + 1]})
                n += 2
                n, nmax = getnum(n, unpacked)
                n, nmin = getnum(n, unpacked)
                params.append({"min": nmin, "max": nmax})

            self.set_values(assignment = assignment, params = params)
            # one of these print statements allows dial signal blocking to work!
            # otherwise setting pot value triggers code 26 message to be sent
            #print(f"EXPR1: Assignment {assignment[0]}, Min {params[0]['min']}, Max {params[0]['max']}")
            #print(f"EXPR2: Assignment {assignment[1]}, Min {params[1]['min']}, Max {params[1]['max']}")
            #print(f"EXPR3: Assignment {assignment[2]}, Min {params[2]['min']}, Max {params[2]['max']}")

            return n

    class gnx1_lfo(QObject):

        lfoPotChanged = Signal(int, int, dict, str)  # section, parameter, pot, name

        def __init__(self, parent, ui_device):
            super().__init__()

            self.parent = parent
            self.ui_device = ui_device

            self.ui_device.lfoPotChanged.connect(self.sendExpPots)
            self.ui_device.lfoChanged.connect(self.parent.sendcode26message)
            for x in range(0, 2):
                for m in ["min", "max", "speed","waveform"]:
                    self.ui_device.pots[x][m].valueChanged.connect(self.parent.sendcode26message)
                    pass

        def sendExpPots(self, parameter, pot):  # for expression from ui_device
            names = {0x04: "LFO1 Speed", 0x05: "LFO2 Speed"}
            self.lfoPotChanged.emit(0x0E, parameter, pot, names[parameter])

        # from GNX1      
        def set_values(self, lfos):
            a = {}
            for index, lfo in lfos.items():
                if lfo["speed"] < 0 or lfo["speed"] > 185:
                    e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in LFO Speed ({lfo["speed"]})", buttons = QMessageBox.Ok)
                    self.parent.gnxAlert.emit(e)

                if lfo["waveform"] < 0 or lfo["waveform"] > 2:
                    e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in LFO Waveform ({lfo["waveform"]})", buttons = QMessageBox.Ok)
                    self.parent.gnxAlert.emit(e)

                a[index] = get_expression_assignment_index(lfo["section"], lfo["parameter"] if lfo["section"] != 0xFF else 0xFF) # make parameter 0xFF id section is 0xFF
                if a[index] == None:
                    e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", text = f"Error in LFO Assign Section (Section {lfo["section"]:02X}, Parameter {lfo["parameter"]:02X})", buttons = QMessageBox.Ok)
                    self.parent.gnxAlert.emit(e)

            for index in lfos.keys():
                lfos[index]["assignment"] = a[index]

            self.ui_device.setParameters(lfos)
                
        # decode code 26 values from GNX1
        def get_values(self, n, unpacked):
            n = skip_bytes(n, unpacked, [0x8A, 0x02])
            n, lfo1  = self.get_lfo(n, unpacked, 0)
            n = skip_bytes(n, unpacked, [0x8B, 0x02])
            n, lfo2 = self.get_lfo(n, unpacked, 1)
            self.set_values({0: lfo1, 1: lfo2})
            return n

        def get_lfo(self, n, unpacked, index):
            n, speed = getnum(n, unpacked)
            n, waveform = getnum(n, unpacked)
            n = skip_bytes(n, unpacked, [0x01]) # might be another parameter
            section = unpacked[n]
            parameter = unpacked[n + 1]
            n += 2
            n, max = getnum(n, unpacked)
            n, min = getnum(n, unpacked)
            return n, {"speed": speed, "waveform": waveform, "section": section, "parameter": parameter, "max": max, "min": min}

    # return UI
    def getUI(self):

        path = os.path.abspath(__file__)
        path = path.replace("py", "ui")
        dev_file = QFile(path)

        if not dev_file.open(QIODevice.ReadOnly):
            e = GNXError(icon = QMessageBox.Warning, title = "GNX UI error", text = f"Cannot open {path}: {dev_file.errorString()}", \
                           buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)
        
        loader = QUiLoader()
        loader.registerCustomWidget(StyleDial)
        loader.registerCustomWidget(AmpFace)
        loader.registerCustomWidget(CabFace)

        device = loader.load(dev_file)
        dev_file.close()
        return device

    # MAIN CLASS CODE

    midiPatchChange = Signal(int)      # MIDI patch change 0xCn
   
    def __init__(self, ui = None, midicontrol = None):
        super().__init__()

        self.midicontrol = midicontrol
        self.requested_patch_bank = 0
        self.ui = ui
        if self.midicontrol == None:
            e = GNXError(icon = QMessageBox.Critical, title = "System Error", text = "No MIDI controller specified for GNX1", buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)
        if self.ui == None:
            e = GNXError(icon = QMessageBox.Critical, title = "System Error", text = "No window specified for GNX1", buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)    
        self.midicontrol.register_input_target(self.dispatcher)
        self.midicontrol.register_ports_open(self.ports_open)
        self.midicontrol.register_ports_closed(self.ports_closed)

        self.device_pickup = self.gnx1_pickup(self, self.ui.pickupFace)
        self.device_wah = self.gnx1_wah(self, self.ui.wahFace)
        self.device_compressor = self.gnx1_compressor(self, self.ui.compressorFace)
        self.device_whammy = self.gnx1_whammy(self, self.ui.whammyFace)
        self.device_warp = self.gnx1_warp(self, self.ui.warpFace)
        self.device_green_amp = self.gnx1_amp(self, self.ui.ampGreen, 0x06)
        self.device_red_amp = self.gnx1_amp(self, self.ui.ampRed, 0x08)
        self.device_green_cab = self.gnx1_cab(self, self.ui.cabGreen, 0x07)
        self.device_red_cab = self.gnx1_cab(self, self.ui.cabRed, 0x09)
        self.device_gate = self.gnx1_gate(self, self.ui.gateFace)
        self.device_mod = self.gnx1_mod(self, self.ui.modFace)
        self.device_delay = self.gnx1_delay(self, self.ui.delayFace)
        self.device_reverb = self.gnx1_reverb(self, self.ui.reverbFace)
        self.device_expression = self.gnx1_expression(self, self.ui.expFace)
        self.device_lfo= self.gnx1_lfo(self, self.ui.lfoFace)

        # link up expression pots
        self.device_compressor.compressorPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_compressor.compressorPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_compressor.ui_device.sendExpPots()
        self.device_whammy.whammyPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_whammy.whammyPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_whammy.ui_device.sendExpPots()
        self.device_warp.warpPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_warp.warpPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_warp.ui_device.sendExpPots()
        self.device_red_amp.ampPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_red_amp.ampPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_red_amp.ui_device.sendExpPots()
        self.device_green_amp.ampPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_green_amp.ampPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_green_amp.ui_device.sendExpPots()
        self.device_gate.gatePotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_gate.gatePotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_gate.ui_device.sendExpPots()
        self.device_mod.modPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_mod.modPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_mod.ui_device.sendExpPots()
        self.device_delay.delayPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_delay.delayPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_delay.ui_device.sendExpPots()
        self.device_reverb.reverbPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_reverb.reverbPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_reverb.ui_device.sendExpPots() 
        self.device_lfo.lfoPotChanged.connect(self.device_expression.ui_device.devicePotChanged)
        self.device_lfo.lfoPotChanged.connect(self.device_lfo.ui_device.devicePotChanged)
        self.device_lfo.ui_device.sendExpPots()

        # initialise ui devices
        self.ui.ampGreen.setAmpStyle(0)
        self.ui.ampRed.setAmpStyle(0)

    def midi_resync(self):
        self.setDeviceConnected(False)
        self.resyncing = True
        self.enquire_device()

    deviceConnectedChanged = Signal(bool)
    def setDeviceConnected(self, connected):
        self.device_connected = connected
        self.deviceConnectedChanged.emit(connected)

    def midi_watchdog_bite(self):
        if self.midi_watchdog_bite_count > self.midi_watchdog_bite_count_limit:
            #print("WATCHDOG HAS BITTEN")
            self.midi_resync()
            self.midi_watchdog_bite_count = 0
            self.midi_watchdog.reset()
        else:
            #print(self.midi_watchdog_bite_count, self.device_connected)
            self.midi_watchdog_bite_count += 1
            self.midi_watchdog.reset()
            self.send_keep_alive()

    def send_parameter_change(self, section = None, parameter = None, value = None):
        if section == None or parameter == None or value == None:
            return

        command = [0x2C]    # command prefix for parameter change

        v = compile_number(value)
        
        data = pack_data([0x02, 0x00] + [section, parameter] + v)
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, command + data)
        #print("Sending Message:", msg)
        self.midicontrol.send_message(msg)
        pass

    patchNameChanged = Signal(str, int, int)    
    def setPatchName(self, name):
        if name != None:
            if self.current_patch_name != name or True:
                self.current_patch_name = name
                #print("Changing patch name")
                self.patchNameChanged.emit(name, self.current_patch_bank, self.current_patch_number)
            else:
                pass

    midiChannelChanged = Signal(int)
    def set_midi_channel(self, channel):
        settings.GNXEDIT_CONFIG["midi"]["channel"] = channel
        settings.save_settings()
        self.midiChannelChanged.emit(channel + 1)
        #(f"GNX1 MIDI Channel: {channel:02X}")

    def ports_open(self):
        self.setDeviceConnected(False)
        self.resyncing = True
        self.enquire_device()
        self.midi_watchdog = self.watchdog(timeout = self.midi_watchdog_time, userHandler = self.midi_watchdog_bite)
        self.midi_watchdog.start()

    def ports_closed(self):
        if self.midi_watchdog != None:
            self.midi_watchdog.stop()
        self.setDeviceConnected(False)
        self.resyncing = False
        self.uploading = 0

    # syncing: 
    # enquire_device -> 7E -> request_status (0x05) -> decode06 -> request_patch_names(0x12, 0) -> decode13 -> request_patch_names(0x12, 1) -> decode13 -> 
    # request_ampcab_names(0x07) -> decode08 -> request_current_patch_name(0x20) -> decode 0x21-> acknowledge_patch_name(0x7E) -> patch data follows

    # send code 0x01 device enquiry broadcast to all devices on all channels
    def enquire_device(self):
        #print("Enquiring")
        self.midicontrol.send_message([0xF0, 0x00, 0x00, 0x10, 0x7E, 0x7F, 0x01, 0x00, 0x01, 0x00, 0x00, 0x11, 0xF7])

    def request_status(self):
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x05, 0x00, 0x01])
        self.midicontrol.send_message(msg)

    def request_patch_names(self, bank):        # 0: factory, 1: user
        self.requested_patch_bank = bank
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x12, 0x00, 0x01, bank, 0x00])
        self.midicontrol.send_message(msg)

    # send code 07 request
    def request_ampcab_names(self, subcode):
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x07, 0x00, 0x01, subcode])
        self.midicontrol.send_message(msg)

    def request_current_patch_name(self):
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x20, 0x00, 0x01, 0x02, 0x00, 0x1F])
        self.midicontrol.send_message(msg)

    def send_keep_alive(self):
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x76, 0x20, 0x01, 0x7F])
        self.midicontrol.send_message(msg)

    def acknowledge_current_patch_name(self):
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x7E, 0x00, 0x01, 0x21])
        self.midicontrol.send_message(msg)

    def send_patch_change(self, bank, patch):
        if self.device_connected:
            self.current_patch_bank = bank
            self.current_patch_number = patch
            msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x2D, 0x00, 0x01, bank, patch, 0x00])
            self.midicontrol.send_message(msg)

    # save patch with patch name
    def save_patch(self, name, sourcebank, sourcepatch, targetbank, targetpatch):
        self.setPatchName(name)
        data = [0x01, sourcebank, sourcepatch, targetbank, targetpatch] + [ord(c) for c in name] + [0x00, 0xFF]
        packed = pack_data(data)
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x2E] + packed)
        #print("Sending Message:", msg)
        self.midicontrol.send_message(msg)

    # send patch name
    def sendcode21message(self, name):
        data = [0x01, 0x02, 0x00] + [ord(c) for c in name] + [0x00, 0x00, 0x08, 0x09, 0x7C]
        packed = pack_data(data)
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x21] + packed)
        self.midicontrol.send_message(msg)

    def sendcode26message(self):
        
        expheader = [0x02, 0x02, 0x00, 0x03, 0x80, 0x00, 0x03]
        
        exp1 = [0xFF, 0x00, 0x00, 0x00] # off
        if self.device_expression.ui_device._types[0] != 0:
            exp1 = [factory_expression_assignments[self.device_expression.ui_device._types[0]]["section"], 
                    factory_expression_assignments[self.device_expression.ui_device._types[0]]["parameter"]] + \
                    compile_number(self.device_expression.ui_device.pots[0]["max"].value()) + \
                    compile_number(self.device_expression.ui_device.pots[0]["min"].value())
            
        exp2 = [0xFF, 0x00, 0x00, 0x00] # off
        if self.device_expression.ui_device._types[1] != 0:
            exp2 = [factory_expression_assignments[self.device_expression.ui_device._types[1]]["section"], 
                    factory_expression_assignments[self.device_expression.ui_device._types[1]]["parameter"]] + \
                    compile_number(self.device_expression.ui_device.pots[1]["max"].value()) + \
                    compile_number(self.device_expression.ui_device.pots[1]["min"].value())
            
        exp3 = [0xFF, 0x00, 0x00, 0x00] # off
        if self.device_expression.ui_device._types[2] != 0:
            exp3 = [factory_expression_assignments[self.device_expression.ui_device._types[2]]["section"], 
                    factory_expression_assignments[self.device_expression.ui_device._types[2]]["parameter"]] + \
                    compile_number(self.device_expression.ui_device.pots[2]["max"].value()) + \
                    compile_number(self.device_expression.ui_device.pots[2]["min"].value())
            
        exp = expheader + exp1 + exp2 + exp3
            
        lfo1header = [0x8A, 0x02]
        lfo1 = compile_number(self.device_lfo.ui_device.pots[0]["speed"].value()) + \
               compile_number(self.device_lfo.ui_device.pots[0]["waveform"].value()) + \
               [0x01] + \
               [factory_expression_assignments[self.device_lfo.ui_device._types[0]]["section"],
                factory_expression_assignments[self.device_lfo.ui_device._types[0]]["parameter"]] + \
                compile_number(self.device_lfo.ui_device.pots[0]["max"].value()) + \
                compile_number(self.device_lfo.ui_device.pots[0]["min"].value())

        lfo2header = [0x8B, 0x02]
        lfo2 = compile_number(self.device_lfo.ui_device.pots[1]["speed"].value()) + \
               compile_number(self.device_lfo.ui_device.pots[1]["waveform"].value()) + \
               [0x01] + \
               [factory_expression_assignments[self.device_lfo.ui_device._types[1]]["section"],
                factory_expression_assignments[self.device_lfo.ui_device._types[1]]["parameter"]] + \
                compile_number(self.device_lfo.ui_device.pots[1]["max"].value()) + \
                compile_number(self.device_lfo.ui_device.pots[1]["min"].value())

        lfo = lfo1header + lfo1 + lfo2header + lfo2

        packed = pack_data(exp + lfo)
        msg = build_sysex(settings.GNXEDIT_CONFIG["midi"]["channel"], self.mnfr_id, self.device_id, [0x26] + packed)
        #print("Sending Message:", msg)
        self.midicontrol.send_message(msg)

    def dispatcher(self, msg):

        try:
            if type(msg) != type(None):
                # check for patch change
                if msg[0] == 0xC0 | settings.GNXEDIT_CONFIG["midi"]["channel"]:
                    self.midiPatchChange.emit(msg[1])

                elif msg[0] == 0xF0:      # system exclusive
                    #print("Message ({:d}): {:d} bytes received".format(received_count, len(sbytes)) )
                    #print("MNFR ID: {:02X} DEVICE ID: {:02X} COMMAND: {:02X}".format(msg[3], msg[5], msg[6]) )

                    if compare_array(msg[1:4], self.mnfr_id):             # mnfr code matches
                        if msg[4] == 0x7E:                  # non-realtime
                            if self.device_connected:
                                if msg[5] == settings.GNXEDIT_CONFIG["midi"]["channel"] or msg[5] == 0x7F:    # this or all channels
                                    match msg[6]:
                                        case 0x01:
                                            self.decode01()
                                            self.midi_watchdog_bite_count = 0
                                            #self.midi_watchdog.reset()

                                        case 0x02:                  # CODE 02: Device Response
                                            self.decode02(msg)
                                            self.midi_watchdog_bite_count = 0
                                            #self.midi_watchdog.reset()
                                        case _:
                                            e = GNXError(icon = QMessageBox.Warning, title = "System Exclusive Error", \
                                                    text = f"Non-Realtime Message[6] code not recognised {msg}", \
                                                    buttons = QMessageBox.Ok)
                                            self.gnxAlert.emit(e)
                                

                        elif (msg[4] == 0x7F or msg[6] == 0x02 or msg[4] == settings.GNXEDIT_CONFIG["midi"]["channel"]) and (msg[5] == self.device_id ):

                            if self.device_connected:
                                self.midi_watchdog_bite_count = 0
                                #self.midi_watchdog.reset()

                                match msg[6]:
                                    case 0x02:                  # CODE 02: Device Response
                                        self.decode02(msg)
                                    
                                    case 0x06:                  # CODE 06: Status Response
                                        self.decode06(msg)
                                    
                                    case 0x08:                  # CODE 08: Amp/Cab Names
                                        self.decode08(msg)

                                    case 0x0A:                  # CODE 0A: Devide Status
                                        self.decode0A(msg)

                                    case 0x13:                  # CODE 13: Patch Names
                                        self.decode13(msg)

                                    case 0x21:                  # CODE 21: Current Patch Name
                                        self.decode21(msg)

                                    case 0x22:                  # CODE 22: End of Patch Dump
                                        self.decode22(msg)

                                    case 0x24:
                                        self.decode24(msg)      # CODE 24: Patch Dump

                                    case 0x26:                  # CODE 26: LFO and Expression Pedals
                                        self.decode26(msg)

                                    case 0x28:                  # CODE 28: ???
                                        self.decode28(msg)

                                    case 0x2C:                  # CODE 2C: Parameters
                                        self.decode2C(msg)

                                    case 0x2A:                  # CODE 2A: Custom Amps and Cabs
                                        self.decode2A(msg)

                                    case 0x2D:                  # CODE 2D: Current patch number
                                        self.decode2D(msg)

                                    case 0x2E:                  # CODE 2E: Patch name changed (saved)
                                        self.decode2E(msg)
                                    
                                    case 0x7E:
                                        self.decode7E(msg)
                                        pass                    # acknowledged

                                    case 0x7F:                  # checksum error
                                        self.resyncing = False
                                        self.uploading = 0
                                        e = GNXError(icon = QMessageBox.Warning, title = "GNX System Exclusive Error", \
                                                text = f"Error code received {msg}",\
                                                buttons = QMessageBox.Ok)
                                        self.gnxAlert.emit(e)


                                    case _:
                                        self.resyncing = False
                                        self.uploading = 0
                                        e = GNXError(icon = QMessageBox.Warning, title = "GNX System Exclusive Error", \
                                                text = f"Message[{msg[6]}] code not recognised {msg}",\
                                                buttons = QMessageBox.Ok)
                                        self.gnxAlert.emit(e)
                    
                            else:       # device not connected
                                match msg[6]:
                                    case 0x02:                  # CODE 02: Device Response
                                        self.decode02(msg)
                                                                       
                                    case 0x7E:
                                        self.decode7E(msg)
                                        pass                    # acknowledged

                                    case 0x7F:                  # checksum error
                                        e = GNXError(icon = QMessageBox.Warning, title = "GNX System Exclusive Error", \
                                                text = f"Error code received {msg}",\
                                                buttons = QMessageBox.Ok)
                                        self.gnxAlert.emit(e)

                                    case _:
                                        e = GNXError(icon = QMessageBox.Warning, title = "GNX System Exclusive Error", \
                                                text = f"Message[6] code not recognised {msg}",\
                                                buttons = QMessageBox.Ok)    
                                        self.gnxAlert.emit(e)     
                    else:
                        x  = compare_array(msg[1:4], self.mnfr_id)
                        pass

        except GNXError as e:
            self.gnxAlert.emit(e)

        except Exception as e:
            e = GNXError(icon = QMessageBox.Warning, title = "GNX Message Error", text = f"Unrecognised message {msg}", buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)

        return False

    # unpack GNX1 message where 8-byte blocks contain 1 byte with most significant bits + 7 x 7-bit bytes
    def unpack(self, pint):
        unpacked = []
        block = 0
        mask = 0b10000000
        n = 0

        while (block + n) < len(pint):
            if n == 0:
                bit8 = pint[block + n]          # first byte contains MSBs of subsequent 7 bytes
            else:
                b8 = bit8 & (mask >> n)         # MSBs packed bit 7  = data byte 0, bit 0 = data byte 7
                data = pint[block + n]
                if b8:
                    data = data | 0b10000000

                unpacked.append(data)

            n += 1
            if n == 8:
                n = 0
                block += 8  

        return unpacked
    
    def printpacked(self, msg, compareto, comment, logfile):
        
        unpacked = self.unpack(msg[7:-1])
        if comment == None:
            comment = "No comment"

        newbytes = []
        bcount = 0

        if logfile != None:
            flog = open(logfile, "a")
            flog.write(comment + "\t")

        for s in unpacked:
            newbytes.append(s)
            diff = False
            
            if compareto != None and self.lastbytes != None and compareto < len(self.lastbytes) and bcount < len(self.lastbytes[compareto]):
                if self.lastbytes[compareto][bcount] != s:
                    diff = True
            if diff:
                print("\033[7m{:02X}\033[m".format(s), end = " ")
                if logfile != None:
                    flog.write("\"[{:02X}]\"\t".format(s))
            else:
                print("{:02X}".format(s), end = " ")
                if logfile != None:
                    flog.write("\"{:02X}\"\t".format(s))
            
            bcount += 1
            if bcount % 32 == 0:
                print()

        if logfile != None:
            flog.write("\n")
            flog.close()

        print()
        if compareto != None:
            if self.lastbytes == None:
                self.lastbytes = []
            while len(self.lastbytes) < (compareto + 1):
                self.lastbytes.append([])
            self.lastbytes[compareto] = newbytes.copy()


    # CODE 02: Device Response
    def decode02(self, msg):
        # switch to announced channel unless locked
        if not self.device_connected:
            if settings.GNXEDIT_CONFIG["midi"]["lockchannel"] == None:
                self.set_midi_channel(msg[9])
            
            self.setDeviceConnected(True)

            # resync
            self.request_status()

    # CODE 06: Device Status
    def decode06(self, msg):
        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        pint = msg[7:-1]
        unpacked = self.unpack(pint[:-1])

        self.current_patch_bank = unpacked[10]
        self.current_patch_number = unpacked[11]

        #print("CODE 06: Setting Patch")
        self.setPatchName(None)

        if self.resyncing:
            self.requested_patch_bank = 0
            self.request_patch_names(self.requested_patch_bank)     # factory patch names

    # CODE 08: Amp/Cab Names
    def decode08(self, msg):
        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        # self.printpacked(msg, None, None, None)
        pint = msg[7:-1]
        unpacked = self.unpack(pint[:-1])       # chop off final 00 to avoid extra array element

        ntype = unpacked[1]                     # name type: 0 = basic, 1 = user
        ncount = unpacked[5]                    # number of names in list

        amp_names = {}
        cab_names = {}

        n = 6
        k = 0
        while k < ncount:
            idx = unpacked[n]
            name = "".join(map(chr, unpacked[n + 1: n + 7]))
            amp_names[idx] = name

            self.device_green_amp.ui_device.set_user_name(idx, name)
            self.device_red_amp.ui_device.set_user_name(idx, name)

            n += 8
            k += 1

        n += 2
        ncount = unpacked[n]
        n += 1
        k = 0

        while k < ncount:
            idx = unpacked[n]
            name = "".join(map(chr, unpacked[n + 1: n + 7]))
            cab_names[idx] = name

            self.device_green_cab.ui_device.set_user_name(idx, name)
            self.device_red_cab.ui_device.set_user_name(idx, name)

            n += 8
            k += 1

        #print("AMP/CAB NAMES:", amp_names, cab_names)

        if self.resyncing:
            self.request_current_patch_name()

    # CODE 0A: Device Status
    def decode0A(self, msg):
        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        #self.printpacked(msg, 0, "CODE 0A", "code0A.csv")
        
    # CODE 13: User Patch Names
    def decode13(self, msg):
        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        pint = msg[7:-1]
        unpacked = self.unpack(pint[:-1])       # chop off final 00 to avoid extra array element

        self.user_patch_names = "".join(map(chr, unpacked[2:])).split('\x00')

        self.gnxPatchNamesUpdated.emit(self.requested_patch_bank, self.user_patch_names)

        if self.resyncing:
            if self.requested_patch_bank == 0:
                self.requested_patch_bank = 1
                self.request_patch_names(self.requested_patch_bank)     # user
            else:
                self.request_ampcab_names(0x01)
        
    # CODE 21: Current Patch Name
    def decode21(self, msg):
        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        pint = msg[7:-1]
        unpacked = self.unpack(pint)

        #print("CODE 21: Setting Patch Name")
        self.setPatchName("".join(map(chr, unpacked[3:])).split('\x00')[0])       # "".join(map(chr, unpacked[3: 9]))

        if self.resyncing:
            self.acknowledge_current_patch_name()

    # CODE 22: End of patch dump
    def decode22(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        if self.resyncing:
            self.resyncing = False

    # CODE 24: Patch Dump
    def decode24(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        self.code24data = msg.copy()     # for saving to library

        pint = msg[7:-1]
        unpacked = self.unpack(pint)
        n = 0

        n = skip_bytes(n, unpacked, [0x02, 0x02])
        n += 1  # can be 0x00 or 0x09 - 0x09 seems to be after error
        n = skip_bytes(n, unpacked, [0x10, 0x00, 0x00, 0x00, 0x00, 0x00])
        # pickup n = 9
        n = skip_bytes(n, unpacked, [0x50, 0x01, 0x01, 0x90])
        n = self.device_pickup.get_values(n, unpacked)
        # wah
        n = skip_bytes(n, unpacked, [0x51, 0x02, 0x01, 0xC3])
        n = self.device_wah.get_values(n, unpacked)
        # compressor
        n = skip_bytes(n, unpacked, [0x52, 0x03, 0x01, 0xF4])
        n = self.device_compressor.get_values(n, unpacked)
        #whammy
        n = skip_bytes(n, unpacked, [0x53, 0x04, 0x03])
        n += 1 # skip 0x84 (Whammy), 0x85 (IPS), 0x86 (Detune), 0x87 (Pitch)
        n = self.device_whammy.get_values(n, unpacked)
        #warp
        n = skip_bytes(n, unpacked, [0x28, 0x05, 0x00, 0xC8])
        n = self.device_warp.get_values(n, unpacked)
        # green amp
        n = skip_bytes(n, unpacked, [0x3C, 0x06, 0x01, 0x2C])
        n = self.device_green_amp.get_values(n, unpacked)
        # green cab
        n = skip_bytes(n, unpacked, [0x3D, 0x07, 0x01, 0x5E])
        n = self.device_green_cab.get_values(n, unpacked)
        # red amp
        n = skip_bytes(n, unpacked, [0x3C, 0x08, 0x01, 0x2C])
        n = self.device_red_amp.get_values(n, unpacked)
        # red cab
        n = skip_bytes(n, unpacked, [0x3D, 0x09, 0x01, 0x5E])
        n = self.device_red_cab.get_values(n, unpacked)
        # gate
        n = skip_bytes(n, unpacked, [0x54, 0x0A, 0x02])
        n += 1 # skip 0x26 (Silencer), 0x27 (Pluck)
        n = self.device_gate.get_values(n, unpacked)
        # modulation
        n = skip_bytes(n, unpacked, [0x55, 0x0B])
        n += 1 # skip 0x03 or 0x04
        n += 1 # skip 0xE8 (Chorus), etc
        n = self.device_mod.get_values(n, unpacked)
        # delay
        n = skip_bytes(n, unpacked, [0x56, 0x0C, 0x02, 0x58])
        n = self.device_delay.get_values(n, unpacked)
        # reverb
        n = skip_bytes(n, unpacked, [0x57, 0x0D, 0x02, 0xBD])
        n = self.device_reverb.get_values(n, unpacked)
        pass
        # remainder
        #self.print_remainder(n, unpacked, "CODE 24 REMAINDER")
        n = skip_bytes(n, unpacked, [0x14, 0x0E, 0x00, 0x64, 0x06, 0x00])
        n += 1 #Volume PRE value (modified by Pedal and LFO)
        n += 1 #Volume POST value (modified by Pedal and LFO)
        n += 1 #Amp Footswitch setting
        n += 1 #LFO1 Speed
        n += 1 #LFO2 Speed
        n = skip_bytes(n, unpacked, [0x02, 0x0F, 0x00, 0x02, 0x00])


    # CODE 26: LFO and Expression Pedals
    def decode26(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        self.code26data = msg.copy()     # for saving to library

        pint = msg[7:-1]
        unpacked = self.unpack(pint)
        n = 0
        n = skip_bytes(n, unpacked, [0x02, 0x02])
        n += 1  # can be 0x00 or 0x09  - 0x09 seems to be after error
        n = skip_bytes(n, unpacked, [0x03, 0x80, 0x00, 0x03])
        n = self.device_expression.get_values(n, unpacked)
        n = self.device_lfo.get_values(n, unpacked)


    # CODE 28: Unknown
    def decode28(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        self.code28data = msg.copy()     # for saving to library

    # CODE 2A: Custom Amps and Cabs
    def decode2A(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        if self.code2Adata == None:
            self.code2Adata = {}
        self.code24data[f"{msg[11]:02X}{msg[12]:02X}"] = msg.copy()     # for saving to library

        pint = msg[7:-1]
        unpacked = self.unpack(pint)

        if compare_array([0x3C, 0x06], unpacked[3:5]):      # GREEN Amp
            self.device_green_amp.get_values2A(unpacked)
        elif compare_array([0x3C, 0x08], unpacked[3:5]):    # RED Amp
            self.device_red_amp.get_values2A(unpacked)
        elif compare_array(unpacked[3:5], [0x3D, 0x07]):
            self.device_green_cab.get_values2A(unpacked)
        elif compare_array(unpacked[3:5], [0x3D, 0x09]):
            self.device_red_cab.get_values2A(unpacked)

        # self.printpacked(msg, None, None, None)
        pass

    # CODE 2C: Parameters
    def decode2C(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        pint = msg[7:-1]
        unpacked = self.unpack(pint)

        section = unpacked[2]
        parameter = unpacked[3]
        n, value = getnum(4, unpacked)

        #print(f"Section {section} parameter {parameter} value {value}")

        match section:      # section code
            case 0x01:      # pickup
                self.device_pickup.parameter_change(parameter, value) 
            
            case 0x02:      # wah
                self.device_wah.parameter_change(parameter, value) 

            case 0x03:      # compressor
                self.device_compressor.parameter_change(parameter, value) 

            case 0x04:      # whammy
                self.device_whammy.parameter_change(parameter, value) 

            case 0x05:      # warp
                self.device_warp.parameter_change(parameter, value)        

            case 0x06:      # green amp
                self.device_green_amp.parameter_change(parameter, value)

            case 0x07:      # green cab
                self.device_green_cab.parameter_change(parameter, value)

            case 0x08:      # red amp
                self.device_red_amp.parameter_change(parameter, value)

            case 0x09:      # red cab
                self.device_red_cab.parameter_change(parameter, value)

            case 0x0A:      # noise gate
                self.device_gate.parameter_change(parameter, value)

            case 0x0B:      # chorus/mod
                self.device_mod.parameter_change(parameter, value) 

            case 0x0C:      # delay
                self.device_delay.parameter_change(parameter, value) 

            case 0x0D:      # reverb
                self.device_reverb.parameter_change(parameter, value)

            case 0x0E:      # pedal value, not used
                #print("CODE 0E RECEIVED")
                #self.printpacked(msg, 0, "CODE 0E", "code0E.csv")
                pass

            case _:
                e = GNXError(icon = QMessageBox.Warning, title = "Parameter Error", \
                                                text = f"Received parameter change not recognised {section}", \
                                                buttons = QMessageBox.Ok)
                self.gnxAlert.emit(e)

        self.send_keep_alive()

    # CODE 2D: Current patch number has changed
    def decode2D(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return

        pint = msg[7:-1]
        unpacked = self.unpack(pint)
        bank = unpacked[1]
        patch = unpacked[2]

        #print(f"CODE 2D Bank: {bank} Patch: {patch}")

        self.current_patch_bank = bank
        self.current_patch_number = patch

        # resync
        self.resyncing = True
        self.request_current_patch_name()

    # CODE 2E: Patch name changed (saved)
    def decode2E(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return

        pint = msg[7:-1]
        unpacked = self.unpack(pint)

        self.current_patch_bank = unpacked[2]
        self.current_patch_number = unpacked[3]

        name = ""
        n = 4
        while unpacked[n] != 0:
            name += chr(unpacked[n])
            n += 1

        #print(f"PATCH SAVED: Bank {self.current_patch_bank} Patch {self.current_patch_number} Name {name}")

        self.user_patch_names[self.current_patch_number] = name
        self.setPatchName(name)
        pass

    # CODE 7E: e.g: current patch number has not changed
    def decode7E(self, msg):

        if not self.device_connected or msg[self.midi_channel_offset] != settings.GNXEDIT_CONFIG["midi"]["channel"]:
            return
        
        pint =msg[7:-2]
        unpacked = self.unpack(pint)
        if compare_array(unpacked, [0x01, 0x76, 0x00]):
            # patch number has not changed?
            pass #TODO: what exactly is this?
        
        elif compare_array(unpacked, [0x01, 0x21, 0x00]):
            if self.uploading == 1:
                self.uploading += 1
                self.midicontrol.send_message(self.code24data)

        elif compare_array(unpacked, [0x01, 0x24, 0x00]):
            if self.uploading == 2:
                self.uploading += 1
                self.midicontrol.send_message(self.code2Adata["3C06"])

        elif compare_array(unpacked, [0x01, 0x26, 0x00]):
            if self.uploading == 7:
                self.uploading += 1
                self.midicontrol.send_message(self.code28data)

        elif compare_array(unpacked, [0x01, 0x28, 0x00]):
            if self.uploading == 8:
                self.uploading = 0
                self.midicontrol.send_code22

        elif compare_array(unpacked, [0x01, 0x2A, 0x00]):
            # patch name change acknowledged
            #print("Patch change acknowledged", msg)
            if self.uploading == 3:
                self.uploading += 1
                self.midicontrol.send_message(self.code2Adata["3D07"])
            elif self.uploading == 4:
                self.uploading += 1
                self.midicontrol.send_message(self.code2Adata["3C08"])
            elif self.uploading == 5:
                self.uploading += 1
                self.midicontrol.send_message(self.code2Adata["3D09"])
            elif self.uploading == 6:
                self.uploading += 1
                self.midicontrol.send_message(self.code26data)

        elif compare_array(unpacked, [0x01, 0x2C, 0x00]):
            # parameter change acknowledged
            #print("Parameter change acknowledged", msg)
            pass

        elif compare_array(unpacked, [0x01, 0x2D, 0x00]):
            # patch change acknowledged - get patch dump
            self.resyncing = True
            self.request_current_patch_name()

        elif compare_array(unpacked, [0x01, 0x2E, 0x00]):
            # patch name change acknowledged
            pass
    
        else:
            e = GNXError(icon = QMessageBox.Warning, title = "GNX1 System Exclusive", text = f"Code 7E unrecognised: {msg}, {unpacked}", \
                buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)
        pass

    def save_patch_to_gnx(self):
        ui_file_name = "src/ui/savepatchtognxdialog.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            e = GNXError(icon = QMessageBox.Alert, title = "Save Patch To GNX Error", \
                           text = f"Cannot open {ui_file_name}: {ui_file.errorString()}", buttons = QMessageBox.Ok)
            self.gnxAlert.emit(e)
            return

        loader = QUiLoader()
        self.save_patch_to_gnx_dialog = loader.load(ui_file)

        ui_file.close()
        targetCB = self.save_patch_to_gnx_dialog.findChild(QComboBox, "targetComboBox")

        p = 0
        for  n in self.user_patch_names:
            targetCB.addItem(f"{(p + 1):02.0f}: {n}", p)                
            if self.current_patch_number == p:
                    targetCB.setCurrentIndex(p)
            p += 1

        inputName = self.save_patch_to_gnx_dialog.findChild(QLineEdit, "inputName")
        inputName.setText(self.current_patch_name)

        self.save_patch_to_gnx_dialog.accepted.connect(self.save_patch_to_gnx_dialog_accepted)
        self.save_patch_to_gnx_dialog.rejected.connect(self.save_patch_to_gnx_dialog_rejected)
        self.save_patch_to_gnx_dialog.setParent(self.ui, Qt.Dialog)
        self.save_patch_to_gnx_dialog.show()

    def save_patch_to_gnx_dialog_accepted(self):
        targetCB = self.save_patch_to_gnx_dialog.findChild(QComboBox, "targetComboBox")
        inputName = self.save_patch_to_gnx_dialog.findChild(QLineEdit, "inputName")
        patch = targetCB.currentIndex()
        bank = 1 # user
        name = inputName.text()
        
        # save patch
        self.current_patch_bank = bank
        self.current_patch_number = patch
        self.save_patch(name, 0x02, 0x00, bank, patch)
        self.patchNameChanged.emit(name, self.current_patch_bank, self.current_patch_number)

    def save_patch_to_gnx_dialog_rejected(self):
        pass

    
    def print_remainder(self, n, unpacked, text):
        print(text)
        if self.last_extra == None:
            self.last_extra = unpacked[n:]

        xc = 0
        for x in self.last_extra:
            if xc < len(self.last_extra):
                if self.last_extra[xc] == unpacked[n + xc]:
                    print(f"{unpacked[n + xc]:02X}", end = " ")
                else:
                    print(f"\033[7m{unpacked[n + xc]:02X}\033[m", end = " ")
            else:
                print("**", end = " ")
            xc += 1
        
        print()
        self.last_extra = unpacked[n:]

    def msg2hexstring(self, msg):
        s = ""
        for x in msg:
            s+= f"{x:02X}"
        return s
    
    def hexstring2msg(self, s):
        msg = []
        n = 2
        hs = [s[i:i + n] for i in range(0, len(s), n)]

        for hx in hs:
            msg.append(int(hx, 16))

        # TODO: check bank and patch numbers 02 00
        # replace MIDI channel
        msg[4] = settings.GNXEDIT_CONFIG["midi"]["channel"]

        # recalculate checksum
        cx = 0
        i = 1
        while i < len(msg) - 2:
            cx = cx ^ msg[i]
            i += 1

        msg[len(msg) - 1] = cx

        return msg

    def serialise_to_file(self):
        s = ""
        blocks = [self.code24data, self.code2A["3C06"], self.code2A["3D07"], self.code2A["3C08"], self.code2A["3D09"], self.code26data, self.code28data]
        for b in blocks:
            s += "|" if len(s) > 0 else ""
            s += self.msg2hexstring(b)

    def deserialise_from_file(self, data, name):

        blocks = data.split("|")
        msg0 = self.hexstring2msg(blocks[0])
        self.code24data = msg0
        msg1 = self.hexstring2msg(blocks[1])
        self.code2Adata["3C06"] = msg1
        msg2 = self.hexstring2msg(blocks[2])
        self.code2Adata["3D07"] = msg2
        msg3 = self.hexstring2msg(blocks[3])
        self.code2Adata["3C08"] = msg3
        msg4 = self.hexstring2msg(blocks[4])
        self.code2Adata["3D09"] = msg4
        msg5 = self.hexstring2msg(blocks[5])
        self.code26data = msg5
        msg6 = self.hexstring2msg(blocks[6])
        self.code28data = msg6

        self.resyncing = False
        self.uploading = 1      # indicates upload phase

        # send patch name to buffer

        self.sendcode21message(name)    # acknowledgement will trigger next blocks




