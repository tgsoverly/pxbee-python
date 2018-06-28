import xbee, time

def format_eui64(addr):
    return ':'.join('%02x' % b for b in addr)

def format_packet(p):
    type = 'Broadcast' if p['broadcast'] else 'Unicast'
    print("%s message from EUI-64 %s (network 0x%04X)" %
    (type, format_eui64(p['sender_eui64']), p['sender_nwk']))
    print("from ep 0x%02X to ep 0x%02X, cluster 0x%04X, profile 0x%04X:" %
    (p['source_ep'], p['dest_ep'], p['cluster'], p['profile']))
    print(p['payload'],"\n")

def network_status():
    # If the value of AI is non zero, the module is not connected to a network
    return xbee.atcmd("AI"))

print("Joining network as a router...")
xbee.atcmd("NI", "Router")
network_settings = {"CE": 0, "ID": 0x3332, "EE": 0}
for command, value in network_settings.items():
    xbee.atcmd(command, value)
xbee.atcmd("AC") # Apply changes
time.sleep(1)

while network_status() != 0:
    time.sleep(0.1)
print("Connected to Network\n")

last_sent = time.ticks_ms()
interval = 5000 # How often to send a message

# Start the transmit/receive loop
print("Sending temp data every {} seconds".format(interval/1000))

while True:
    p = xbee.receive()
    if p:
        format_packet(p)
    else:
        # Transmit temperature if ready
        if time.ticks_diff(time.ticks_ms(), last_sent) > interval:
            temp = "Temperature: {}C".format(xbee.atcmd("TP"))
            print("\tsending " + temp)
            try:
                xbee.transmit(xbee.ADDR_COORDINATOR, temp)
            except Exception as err:
                print(err)
            last_sent = time.ticks_ms()
        time.sleep(0.25)
