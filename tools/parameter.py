def pack_data(data):
    packed = []
    pc = 0          # packet counter
    for d in data:
        if pc == 0:
            packet = []
            msb = 0x00
            msmask = 0b01000000     # msb mask starts left == first

        m = d & 0b10000000          # boes byte have bit 8 se
        if m > 0:
            msb = msb | msmask

        packet.append(d & 0b01111111)

        # next byte
        pc += 1
        msmask = msmask >> 1

        # next packet
        if pc == 8:
            pc = 0
            packet.insert(0, msb)
            packed += packet

    if pc > 0:                      # partial packet remains
        packet.insert(0, msb)
        packed += packet            

    return packed

def send_parameter_change(self, section = None, parameter = None, value = None):
    if section == None or parameter == None or value == None:
        return
    print("Value:", value)
    command = [0x2C, 0x00, 0x02]    # command prefix for parameter change

    # split value into 8 bit bytes
    v =[]
    n = value
    while n > 0:
        d = n % 256
        v.append(d)
        n = (n // 256)

    if len(v) > 1:
        v.append(0b10000000 | len(v))   # signals multi-byte number

    #reverse the order
    v = v[::-1]

    data = self.pack_data([section, parameter] + v)
    print(v, data, self.unpack(data))
    msg = self.build_sysex(command + data)
    print("Message:", msg)
    self.midicontrol.send_message(msg)
    pass


# split value into 8 bit bytes
v =[]
n = 129
while n > 0:
    d = n % 256
    v.append(d)
    n = (n // 256)

if len(v) > 1:
    v.append(0b10000000 | len(v))   # signals multi-byte number

#reverse the order
v = v[::-1]

print(pack_data(v))