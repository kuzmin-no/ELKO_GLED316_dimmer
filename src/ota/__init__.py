import uasyncio as asyncio

from sys import path
path.insert(1, '/ota')

import ap_mode
ssid = 'RPI_Pico'
psk_key = 'PASSWORD'
print("Starting AP mode")
local_ip = ap_mode.start_ap_mode(ssid, psk_key)

import dns_server
import web_server
import serial
from ftpdlite import FTPd

loop = asyncio.get_event_loop()

# Start telnet to serial service
global serial_port
serial_port = serial.Serial()
web_server.define_serial_port(serial_port)
loop.create_task(asyncio.start_server(serial_port.handle_client, local_ip, 23))

# Start Web server # https://github.com/erikdelange/MicroPython-HTTP-Server/
loop.create_task(web_server.app.start())

# Start Captive DNS server
loop.create_task(dns_server.CaptiveDNSServer().run(local_ip))

# Start ftp service # https://github.com/DavesCodeMusings/ftpdlite
ftp_server = FTPd(host=local_ip)
ftp_server.add_account("ftpadmin:ftpadmin")
ftp_server.run(loop)
