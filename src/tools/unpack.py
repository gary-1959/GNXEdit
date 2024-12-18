
def toint(s):
    try:
        v = int("0x" + s.lower(), 16)
    except Exception:
        return 0
    return v

packed = "00 01 03 00 48 59 42 52 \
09 49 44 00 7F 08 09 29 \
00 00"

pint = list(map(toint, packed.split(" ")))
unpacked = []

byte = 0
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