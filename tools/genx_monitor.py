import mido

BYTES = 0
PACKED = 1
LINCOMP = 2
LINPACKED = 3
RAW = 4
print_mode = PACKED

lastbytes = None

def toint(s):
    try:
        v = int(s, 16)
    except Exception:
        return 0
    return v

def printlin(sbytes):

    global lastbytes
    newbytes = []
    # 0 - 2: mnfr code (00, 00, 10)
    # 3 : midi channel
    # 4 : device code (56)
    # 5 : command code
    # last byte checksum

    command_name = ""
    match sbytes[5]:
        case 0x7F:
            command_name = "ERROR"
        case 0x7E:
            command_name = "ACKNOWLEDGE"
        case 0x26:
            command_name = "EXPRESSION ASSIGN"
        case 0x2C:
            command_name = "PARAMETER"
        case 0x2D:
            command_Name = "PATCH CHANGE"
        case _:
            command_name = ""

    #command_name += " ({:02X})".format(sbytes[5])

    print("CODE: {:02X} ({:s})".format(sbytes[5], command_name))
    blen = 8
    i = blen
    bcount = 0
    for s in sbytes[6:-1]:
        newbytes.append(s)
        diff = False
        if lastbytes != None and bcount < len(lastbytes):
            if lastbytes[bcount] != s:
                diff = True
        if diff:
            print("\033[7m{:02X}\033[m".format(s), end = " ")
        else:
            print("{:02X}".format(s), end = " ")
        
        # limit line length
        i -= 1
        if i == 0:
            print("|", end = " ")
            i = blen
            #print()

        bcount += 1

    print()
    lastbytes = newbytes.copy()

def printbytes(prefix, sbytes):
    # 0 - 2: mnfr code (00, 00, 10)
    # 3 : midi channel
    # 4 : device code (56)
    # 5 : command code
    # last byte checksum

    command_name = ""
    match sbytes[5]:
        case 0x7F:
            command_name = "ERROR"
        case 0x7E:
            command_name = "ACKNOWLEDGE"
        case 0x26:
            command_name = "EXPRESSION ASSIGN"
        case 0x2C:
            command_name = "PARAMETER"
        case 0x2D:
            command_Name = "PATCH CHANGE"
        case _:
            command_name = ""

    #command_name += " ({:02X})".format(sbytes[5])

    print("{:12s}CODE: {:02X} ({:s})".format(prefix, sbytes[5], command_name))
    blen = 16
    i = blen
    print("DATA:", end = " ")
    for s in sbytes[6:-1]:
        print("{:02X}".format(s), end = " ")
        i -= 1
        if i == 0:
            i = blen
            print()
    print()

def printpacked_lin(packed):
    global lastbytes
    unpacked = []
    pint = packed[6:-1]
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
    for s in unpacked:
        newbytes.append(s)
        diff = False
        if lastbytes != None and bcount < len(lastbytes):
            if lastbytes[bcount] != s:
                diff = True
        if diff:
            print("\033[7m{:02X}\033[m".format(s), end = " ")
        else:
            print("{:02X}".format(s), end = " ")

        bcount += 1

    print()
    lastbytes = newbytes.copy()

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
    print("{0:<25}{1:<25}".format(strh, stra))
    print("Input length ", len(pint), " Output length: ", len(unpacked) )

#print(mido.get_output_names())
#print(mido.get_input_names())


# LINE A
# GENX1 output goes to loopMIDI OUT (input), so loopMIDI OUT (output) is the input here
# which is passed to the USB output

innames = mido.get_input_names()
outnames = mido.get_output_names()
for n in outnames:
    if n.startswith("USB MIDI"):
        outpA = mido.open_output(n)
    elif n.startswith("loopMIDI IN"):
        outpB = mido.open_output(n)


for n in innames:
    if n.startswith("USB MIDI"):
        inpB = mido.open_input(n)
    elif n.startswith("loopMIDI OUT"):
        inpA = mido.open_input(n)

print("MONITORING")
while True:
    for msgA in inpA.iter_pending():
        if msgA.type == "sysex":
            if msgA.data[5] == 118:
                pass
            else:
                
                if print_mode == PACKED:
                    print("--------------PACKED-----------------")
                    printpacked("TRANSMIT", msgA.data)
                elif print_mode == BYTES:
                    print("--------------BYTES-----------------")
                    printbytes("TRANSMIT", msgA.data)
                elif print_mode == LINCOMP:
                    printlin(msgA.data)
                elif print_mode == LINPACKED:
                    printpacked_lin(msgA.data)
                elif print_mode == RAW:
                    print("--------------RAW-----------------")
                    print(msgA.data)
        outpA.send(msgA)
        pass

    for msgB in inpB.iter_pending():
        if msgB.type == "sysex":
            if msgB.data[5] == 126 and msgB.data[8] == 118:
                pass
            else:
                if print_mode == PACKED:
                    printpacked("RECEIVED", msgB.data)
                elif print_mode == BYTES:
                    printbytes("RECEIVED", msgB.data)
                elif print_mode == LINCOMP:
                    pass
                elif print_mode == LINPACKED:
                    pass
        outpB.send(msgB)
        pass


