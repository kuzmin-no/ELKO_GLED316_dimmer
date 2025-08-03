from time import sleep
from os import stat
from machine import UART, Pin, reset
import asyncio
import json
from sys import path
import re

def reboot_in_ota_mode():
    print('Rebooting in OTA mode')
    with open("/ota.lck", 'a'):
        pass
    sleep(3)
    reset()

# Check if config exists
try:
    if stat("/app/config.json"):
        pass
except:
    reboot_in_ota_mode()

path.insert(1, '/app')

from mqtt_as import config

# Apply config
with open('/app/config.json') as json_file:
    config_data = json.load(json_file)

config.update(config_data)

def read_uart():
    for i in range(3):
        try:
            buffer = uart.read().decode("ascii").strip()

            # Pressed "press button" and dimmer at the same time -> Reboot
            #
            if buffer == "RES":
                 print('Rebooting')
                 sleep(3)
                 reset()

            # Long press of "press button" until LED start glowing and then dimmer -> AP mode
            #
            if buffer == "LRN":
                reboot_in_ota_mode()

            pow_and_dim = re.match("OK (\d+),(\d+)", buffer)
            if pow_and_dim:
                pow = int(pow_and_dim.group(1))
                dim = int(pow_and_dim.group(2))
                dim_value = int((dim / 100) * 255)
            return pow, dim_value
        except Exception as error:
            #print("An exception occurred:", error)
            uart.write((f"STA\n").encode("ascii"))
            sleep(0.1)
    reset()

async def main():
        await asyncio.sleep(0.2)

async def update():
        await light_mqtt.update_state()


print('Staring UART comm with ELKO GLED 316')
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5), bits=8, parity=None, stop=1)

print('Requesting status from ELKO GLED 316')
(pow, dim) = read_uart()
pow_status = "ON" if pow == 1 else "OFF"
print(f"Current is power: {pow_status} dimmer: {dim}%")

import ha_mqtt
import ha_mqtt_light
from drivers import BasicLightDriver, BrightnessLightDriver

if config["device_type"] == "switch":
    light_mqtt = ha_mqtt_light.HaMqttBasicLight(name=config["device_name"], light=BasicLightDriver(uart), pow_status=pow_status)
else:
    light_mqtt = ha_mqtt_light.HaMqttBrightnessLight(name=config["device_name"], light=BrightnessLightDriver(uart), pow_status=pow_status, dim_status=dim)

print('Starting loop...')
try:
#    asyncio.get_event_loop().run_forever()
    while True:
        asyncio.run(main())
        if uart.any() > 0:
            (pow, dim) = read_uart()
            pow_status = "ON" if pow == 1 else "OFF"
            print(f"Status change from dimmer - power: {pow_status} dimmer: {int((dim / 255) * 100)}%")
            if config["device_type"] == "switch":
                if light_mqtt.current_state['state'] != pow_status:
                    light_mqtt.current_state['state'] = pow_status
                    asyncio.run(update())
            else:
                if (light_mqtt.current_state['state'] != pow_status) or (light_mqtt.current_state['brightness'] != dim):
                    light_mqtt.current_state['state'] = pow_status
                    light_mqtt.current_state['brightness'] = dim
                    asyncio.run(update())
except:
     reset()
finally:
    ha_mqtt.close_client()  # Prevent LmacRxBlk:1 errors
