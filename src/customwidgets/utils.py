# utils.py
#
# GNX Edit general utilities for Digitech GNX1
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

from .factory import factory_expression_assignments

# UTILITIES
# compare two arrays and return True on match
def compare_array(a1, a2):
    if a1 == None or a2 == None:
        return False
    if len(a1) != len(a2):
        return False
    
    i = 0
    while i < len(a1):
        if a1[i] != a2[i]:
            return False
        i += 1
        
    return True

# creates and compares checksum
def sysex_checksum(msg):
    cx = 0
    i = 1
    while i < len(msg) - 2:
        cx = cx ^ msg[i]
        i += 1

    return cx, (cx == msg[i])

# return the variable length number at position n in unpacked byte string
def getnum(n, unpacked):
    v = 0
    b = unpacked[n]
    n += 1
    if b & 0b10000000:
        nbytes = b & 0b01111111
        c = 0
        while c < nbytes:
            v = (v * 256) + unpacked[n]
            n += 1
            c += 1
    else:
        v = b

    return n, v

# skip byes in packed byte array and check values
def skip_bytes(n, unpacked, bytes):
    m = len(bytes)
    if unpacked[n:n + m] != bytes:
        raise Exception(f"Pattern mis-match at {n}")

    n += m
    return n

# compile number into GNX1 multi-byte format
def compile_number(value):
    # split value into 8 bit bytes
    v =[]
    n = value
    if n < 0x80:
        v = [n]
    elif n < 0x100:     # to 0xFF
        v = [0x81, n]
    elif n < 0x10000:   # to  0xFFFF
        v = [0x82, (n // 0x100),  (n % 0x100)]
    else:               # to 0xFFFFFF
        v = [0x83, (n // 0x10000), (n % 0x10000)]

    print(value, v)
    return v

# pack bytes into 1 MSB byte + (up to) 7 data bytes
def pack_data(data):
    packed = []
    pc = 0          # packet counter
    for d in data:
        if pc == 0:
            packet = []
            msb = 0x00
            msmask = 0b01000000     # msb mask starts left == first

        m = d & 0b10000000          # does byte have bit 8 set
        if m > 0:
            msb = msb | msmask

        packet.append(d & 0b01111111)

        # next byte
        pc += 1
        msmask = msmask >> 1

        # next packet
        if pc == 7:
            pc = 0
            packet.insert(0, msb)
            packed += packet

    if pc > 0:                      # partial packet remains
        packet.insert(0, msb)
        packed += packet            

    return packed

def build_sysex(midi_channel, mnfr_id, device_id, data):
    #data is from code to before checksum
    msg = [0xF0] + mnfr_id.copy() + [midi_channel, device_id]
    msg += data
    msg += [0, 0xF7]

    cx, ok = sysex_checksum(msg)
    msg[len(msg) - 2] = cx
    return msg

def get_expression_assignment_index(section, parameter):
    for k, v in factory_expression_assignments.items():
        if v["section"] == section  and v["parameter"] == parameter:
            return k
        
    return None

def printhex(msg):
    for x in msg:
        print(f"{x:02X} ", end = "")
    print()