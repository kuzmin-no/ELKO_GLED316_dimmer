import network

def start_ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass

    local_ip = ap.ifconfig()[0]
    print(f'AP Mode Is Active. IP Address To Connect to: {local_ip}')
    return local_ip
