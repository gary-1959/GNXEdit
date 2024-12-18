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
    if packed[6] != 0x24:   # code 24 only
        return
    
    unpacked = []
    print("MNFR ID: {:02X} DEVICE ID: {:02X} COMMAND: {:02X}".format(packed[3], packed[5], packed[6]) )
    pint = packed[7:-1]
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
    flog.write(comment + "\t")

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

outports = mido.get_output_names()
inports = mido.get_input_names()
pass

#msg = mido.Message('program_change', channel=0, program=6)
#port = mido.open_output(ports[1])
#port.send(msg)

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

#ms.append("F0 00 00 10 7E 7F 01 00 01 00 00 11 F7")           # 01: device enquiry
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7")            # active control
#ms.append("F0 00 00 10 00 56 70 00 01 08 3F F7")
#ms.append("F0 00 00 10 00 56 05 00 01 42 F7")                
#ms.append("F0 00 00 10 00 56 07 00 01 00 40 F7")          # 07:00 Amp and Cabinet Names
#ms.append("F0 00 00 10 00 56 07 00 01 01 41 F7")          # 07:01 Bad?
#ms.append("F0 00 00 10 00 56 07 00 01 02 42 F7")          # 07:02 Bad?
#ms.append("F0 00 00 10 00 56 12 00 01 01 00 54 F7")       # patch names
ms.append("F0 00 00 10 00 56 20 00 01 02 00 1F 7A F7")     # response 21 gets patch name and params (amp?, cab?)
ms.append("F0 00 00 10 00 56 7E 00 01 21 18 F7")           # acknowledge              
#ms.append("F0 00 00 10 00 56 2E 00 01 02 00 02 01 00 00 68 F7") # DIRECT amp model
#ms.append("F0 00 00 10 00 56 2D 00 01 01 00 00 6B F7")
#ms.append("F0 00 00 10 00 56 20 00 01 03 00 1F 7B F7")
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7")  
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7")  
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7")  
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7") 
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7") 
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7") 
#ms.append("F0 00 00 10 00 56 76 20 01 7F 6E F7") 

# change patch to USER 4
#ms.append("F0 00 00 10 00 56 2D 00 01 01 10 00 7B F7")

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
        #print("Sending message:")
        #printbytes(send.bytes())
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
                    printpacked_lin(sbytes, received_count, comment)
                    c += 1
                    received_count += 1
            else:
                time.sleep(1)
                nonecount -= 1
                if nonecount == 0:
                    break
            


