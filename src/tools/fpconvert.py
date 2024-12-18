import struct

def bytes2num(d = [0, 0, 0, 0]): # code followed by ls byte last
    d = d.copy()
    bit8 = 0
    if d[0] in [20, 24]:
        bit8 = 1

    if d[0] == 24:
        d[2] = 0

    d[3] = 0 if d[3] == None else d[3]
    d[2] = 0 if d[2] == None else d[2]

    num16 = 300 + (d[3] | (d[2] << 8) | (bit8 << 7))
    return num16

def num2bytes(n = 0):
    n = n - 300
    lo = n & 0x00ff
    hi = (n & 0xff00) >> 8

    bit8 = 0
    if lo & 0x80:
        bit8 = 1
        lo = lo & 0x7f


    if n < 128:
        return [0, None, None, lo]
    
    elif n >= 128 and n < 256:
        return [24, None, 1, lo]

    else:
        if bit8 == 1:
            return [20, 2, hi, lo]
        else:
            return [16, 2, hi, lo]
        




def eqconvert(offset, d):
    d = d.copy()
    
    mid_freq = 0
    mid = 0
    treble_freq = 0
    treble = 0

    n = offset

    flags = d[n]
    bass = d[n + 2]

    # mid
    n += 3
    if flags & 0b10000:
        dbytes = d[n]       # d[n] contains number of bytes in number

        if dbytes == 1:
            mid_freq = d[n + 1] + 128
            n += 2
        elif dbytes == 2:
            if flags & 0b00100:  # '4' bit flags MSB in lower byte
                mid_freq = (d[n + 1] * 256) + ((0b10000000 | d[n + 2]))
            else:
                mid_freq = (d[n + 1] * 256) + (d[n + 2])
            n += 3
    else:
        mid_freq = d[n]
        n += 1

    mid = d[n]

    # treble
    n += 1
    if flags & 0b00100:
        dbytes = d[n]       # d[n] contains number of bytes in number

        if dbytes == 1:
            treble_freq = d[n + 1] + 128
            n += 2
        elif dbytes == 2:
            if d[n +1] == 32:   # spurious byte - wtf?
                n += 1
            if flags & 0b00001:  # '1' bit flags MSB in lower byte
                treble_freq = (d[n + 1] * 256) + ((0b10000000 | d[n + 2]))
            else:
                treble_freq = (d[n + 1] * 256) + (d[n + 2])
            n += 3
    else:
        treble_freq = d[n]
        n += 1

    treble = d[n]

    bass -= 12
    mid -= 12
    treble -= 12

    mid_freq += 300
    treble_freq += 500

    return {"bass": bass, "mid": mid, "treble": treble, "mid_freq": mid_freq, "treble_freq": treble_freq}

s = "21	100	24	2	9	68	24	2	32	19	8	24"

slist = s.split("\t")
snum = list(map(int, slist))
print(eqconvert(0, snum))


