import mido
from pynput.keyboard import Key, Listener
import time
import os

BREAK = False
lastbytes = []

def on_press(key):
    #print('{0} pressed'.format(key))
    pass

def on_release(key):
    global BREAK
    #print('{0} release'.format(key))
    if key == Key.esc:
        # Stop listener
        BREAK = True
        return False

# Collect events until released
listener = Listener(on_press = on_press, on_release = on_release)
listener.start()

def toint(s):
    return int("0x" + s.lower(), 16)

def tohex(s):
    return hex(int(s.lower(), 16))

def printbytes(sbytes):
    c = 0
    blen = 8
    i = blen
    for s in sbytes:
        if c == 7:          # new line after header
            i = blen
            print()
        print("{:02X}".format(s), end = ' ')
        i -= 1
        if i == 0:
            i = blen
            print()
        c += 1
    print()

def printpacked_lin(packed, compareto, comment):
    global lastbytes, logfile

    if comment == None:
        comment = "No comment"

    # show patch parameters only
    #if packed[6] != 0x24:   # code 24 only
    #    return
    
    unpacked = []
    print("MNFR ID: {:02X} DEVICE ID: {:02X} COMMAND: {:02X}".format(packed[3], packed[5], packed[6]) )
    pint = packed[7:-2]
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

    newbytes = []
    bcount = 0

    flog = open(logfile, "a")
    flog.write(f"{comment}({packed[6]:02X})\t") # comment and command

    for s in unpacked:
        newbytes.append(s)
        diff = False
        
        if compareto != None and lastbytes != None and compareto < len(lastbytes) and bcount < len(lastbytes[compareto]):
            if lastbytes[compareto][bcount] != s:
                diff = True
        if diff:
            print("\033[7m{:02X}\033[m".format(s), end = " ")
            flog.write("\"[{:02X}]\"\t".format(s))
        else:
            print("{:02X}".format(s), end = " ")
            flog.write("\"{:02X}\"\t".format(s))
        
        bcount += 1
        if bcount % 32 == 0:
            print()
    flog.write("\n")
    flog.close()

    print()
    if compareto != None:
        while len(lastbytes) < (compareto + 1):
            lastbytes.append([])
        lastbytes[compareto] = newbytes.copy()

def printpacked(prefix, packed):

    command_name = ""
    match packed[5]:
        case 0x7F:
            command_name = "ERROR"
        case 0x7E:
            command_name = "ACKNOWLEDGE"
        case 0x26:
            command_name = "EXPRESSION ASSIGN"
        case 0x2C:
            command_name = "PARAMETER"
        case 0x2D:
            command_name = "PATCH CHANGE"
        case _:
            command_name = ""

    command_name += " {:02X}".format(packed[5])

    print(prefix, command_name)
    unpacked = []
    pint = packed[6:-1]

    block = 0
    mask = 0b10000000
    n = 0

    flog = open(logfile, "a")
    flog.write(comment + "\t")

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

    i = 8
    strh = ""
    stra = ""

    for s in unpacked:
        strh += "{:02X}".format(s) + " "
        stra += (chr(s) if s >=32 and s <= 127 else ".") + " "

        i -= 1
        if i == 0:
            i = 8
            print(strh, stra)
            strh = ""
            stra = ""

        flog.write("\"{:02X}\"\t".format(s))

    flog.write("\n")
    flog.close()
            
    print("{0:<25}{1:<25}".format(strh, stra))
    print("Input length ", len(pint), " Output length: ", len(unpacked) )

outports = mido.get_output_names()
inports = mido.get_input_names()
pass

# test to receive patch dump from Digitech GENX1
genx1_mnfr_id = [0x00, 0x00, 0x10]
midi_channel = 0x00
outport = None
inport = None
for p in inports:
    if p.startswith("USB"):
        inport = mido.open_input(p)
        break

for p in outports:
    if p.startswith("USB"):
        outport = mido.open_output(p)
        break

ms = []
#ms.append(f"F0 00 00 10 00 56 0E 00 01 49 F7")           # command to send
for i in range(0x00, 0x10):
    m = [0x00, 0x00, 0x10, 0x00, 0x56, 0x11, 0x00, i]
    cx = 0
    for x in m:
        cx = cx ^ x

    m = [0xF0] + m + [cx, 0xF7]
    s = ""
    for x in m:
        s = s + f"{x:02X} "
    
    s = s.strip()
    ms.append(s)

logfile = input("Logfile name: ").lower()
if len(logfile) == 0:
    logfile = "test.csv"

while True:

    comment = input("[Q]uit or Comment: ")
    
    if comment.lower() == "q":
        break

    received_count = 0

    for m in ms:
        
        mns = m.split(" ")
        mhs = list(map(toint, mns))

        send = mido.Message.from_bytes(mhs)
        #print()
        print("Sending message:")
        printbytes(send.bytes())
        #printpacked_lin(send.bytes(), None, comment)
        outport.send(send)
        time.sleep(1)

        nonecount = 5
        c = 1
        while True:
            if BREAK:
                break

            msg = inport.receive(block = False)

            if type(msg) != type(None):
                if msg.type == "sysex":
                    sbytes = msg.bytes()
                    #print("Message ({:d}): {:d} bytes received".format(received_count, len(sbytes)) )
                    #printbytes(sbytes)
                    #printpacked("RECEIVED", msg.data)
                    printpacked_lin(sbytes, received_count, comment)
                    #qprintbytes(sbytes)
                    c += 1
                    received_count += 1
            else:
                time.sleep(1)
                nonecount -= 1
                if nonecount == 0:
                    break
            


