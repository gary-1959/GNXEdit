import mido

from pynput.keyboard import Key, Listener

BREAK = False

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

ports = mido.get_output_names()

#msg = mido.Message('program_change', channel=0, program=6)
#port = mido.open_output(ports[1])
#port.send(msg)

rq = "F0 00 00 10 MM 56 05 00 01 CX F7"
midi = 0

program = 0

last_response = None

port = mido.open_ioport(ports[1])

base_messages = None
while True:
    # purge input
    k = input("[N]ew Message, [Q]uit: ").lower()
     
    if k == "q":
        break

    elif k == "n":
        print("Requesting")

        rqx = rq
        rqx = rqx.replace("MM", "{:02X}".format(midi))

        rqmsg = rqx.split(" ")
        cx = 0
        for i in range(3, 9):
            cx = cx ^ int(rqmsg[i], 16)

        rqx = rqx.replace("CX", "{:02X}".format(cx))    

        rqmsg = rqx.split(" ")
        rqbytes = list(map(toint, rqmsg))

        send = mido.Message.from_bytes(rqbytes)
        port.send(send)

        while True:
            if BREAK:
                BREAK = False
                break

            msg = port.receive(block = False)
            if type(msg) != type(None):
                if msg.type == "sysex":
                    sbytes = msg.bytes()
                    i = 32
                    for s in sbytes:
                        print("{:02X}".format(s), end = ' ')
                        i -= 1
                        if i == 0:
                            i = 32
                            print()
                    print()

                    if last_response == None:
                        last_response = sbytes.copy()
                    else:
                        i = 0
                        for b in sbytes:
                            if b != last_response[i]:
                                print("Byte {:02X} was {:02X} now {:02X}".format(i, last_response[i], b))
                            i += 1

                        last_response = sbytes.copy()

                    break



