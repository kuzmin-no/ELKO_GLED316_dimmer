import uasyncio as asyncio
from machine import UART, Pin, reset
from time import sleep_ms, sleep
from os import remove

"""
ELKO 316 GLED

Commands:

    STA - status of power and dimmer. All arguments will be ignored.
    POW X - set power state, X values can be 0 (off) or 1 (on). The command without argumnets is equial to STA command.
    DIM Y - set dimmer state, Y values can be in the range from 0 to 100. The command without argumnets is equial to STA command.
    VER - firmware version
    BYE - close telnet session
    APP - delete ota.lck file and restart in main app

Reply from dimmer:

OK 0,100 - reply to STA/POW/DIM commands
         - the first digit is power status and it can be 0 (off) or 1 (on)
         - the second digit is dimmer status and can be in the range from 0 to 100 (%)

0.9.36   - reply to VER command, and additional OK reply

ERROR XX,Y - error reply with codes:
             99,2 - command not found
             00,3 - value out of range
             00,1 - value is incorrect

Dimmer special modes:
      Dimmer sends these commands via serial interface when entering in respective mode by user action.

RES - Reset mode is used for firmware upgrade and restart. 
      Press small "push button" and dimmer knob at the same time for 1-3 sec

LRN - Zigbee learn mode.
      Press small "push button" for apporx 10 seconds, when LED flashes release "push button" and press dimmer knob.

"""

class Serial:
    def __init__(self):
        print("Open UART 115200 8N1")
        self.uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5), bits=8, parity=None, stop=1)

    async def handle_client(self, reader, writer):
        print("Connected client to port 23")
        #self.uart.read()
        writer.write("ELKO 316 GLED\nAllowed commands: STA,POW,DIM,VER,APP,RESTART,BYE\n\n".encode("ascii"))
        while True:
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=1)
                data_text = data.strip().decode("ascii").strip().upper()
                if (data_text == "BYE") or not data:
                    print(data_text)
                    break
                elif (data_text == "RESTART"):
                    sleep(2)
                    reset()
                elif (data_text == "APP"):
                    remove('/ota.lck')
                    sleep(2)
                    reset()
                if (len(data_text) >= 3):
                    print(data_text)
                    self.uart.write((data_text + "\n").encode("ascii"))
                    await asyncio.sleep_ms(1)
            except:
                pass
            
            if self.uart.any() > 0:
                reply = self.uart.read().decode("ascii").replace("\r", "\n")
                print(reply.strip())
                writer.write(reply.encode("ascii"))

        writer.close()
        await writer.wait_closed()

    def pow(self, power_status):
            self.uart.write((f"POW {power_status}\n").encode("ascii"))
            sleep_ms(10)
            self.uart.read()

    def dim(self, dimmer_status):
            self.uart.write((f"DIM {dimmer_status}\n").encode("ascii"))
            sleep_ms(10)
            self.uart.read()

    def sta(self):
            self.uart.read()
            self.uart.write(("STA\n").encode("ascii"))
            sleep_ms(100)
            if self.uart.any() > 0:
                return self.uart.read().decode("ascii").replace("\r", "\n").strip()
            else:
                 return None

