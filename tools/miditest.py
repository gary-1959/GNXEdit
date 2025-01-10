import mido
from fpconvert import eqconvert

ports = mido.get_output_names()

#msg = mido.Message('program_change', channel=0, program=6)
#port = mido.open_output(ports[1])
#port.send(msg)

def get_mnfr_id(data):
    return ((data[0] * 128) + data[1]) * 128 + data[2]

# test to receive patch dump from Digitech GENX1
genx1_mnfr_id = 16
port = mido.open_input(ports[1])

base_messages = None
while True:
    # purge input

    k = input("[B]ase Message, [N]ew Message, [F]ile, [Q]uit: ").lower()
    
    if k == "q":
        break

    else:
        messages = []
        while True:
            msg = port.receive()
            if msg.type == 'sysex':
                if get_mnfr_id(msg.data) == genx1_mnfr_id:
                    print("SysEx message received")
                    messages.append(msg.data)

            else:   # send any other message to break
                if len(messages) == 0:
                    continue
                else:
                    print("Break message received")
                    break

        # checking EQ
        offset = 78             # may change if preceeding parameters altered
        print("EQ:")
        print(eqconvert(offset, list(messages[1])))

        # save as base message
        if k == "b":
            base_messages = messages

        if k == "n":

            if base_messages == None:
                base_messages = messages
            else: # do comparison
                changed = False
                try:
                    for i in range(0, len(messages)):
                        for j in range(0, len(messages[i])):
                            if base_messages[i][j] != messages[i][j]:
                                print(f"Message {i}, byte {j}: now {messages[i][j]} was {base_messages[i][j]}")
                                changed =True
                    if not changed:
                        print("No variations found")
                except Exception as e:
                    print("Message length mis-match")

                base_messages = messages

        if k =="f":
            f = open("patch.csv", "w")
            for m in messages:
                s = ""
                cx = 0
                count = 0
                for d in m:
                    count += 1
                    if count < len(m):
                        cx = cx ^ d
                    s += ("\t" if len(s) > 0 else "") + str(d)
                f.write(s + "\r\n")
            f.close()
            print("Data Written to patch.csv")

