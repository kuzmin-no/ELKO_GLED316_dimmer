from machine import Pin, PWM
from time import sleep

class BasicLightDriver:
    def __init__(self, uart):
        self.uart = uart

    def on(self):
        #print("BasicLightDriver: on")
        self.uart.write((f"POW 1\n").encode("ascii"))
        sleep(0.1)
        self.uart.read()

    def off(self):
        #print("BasicLightDriver: off")
        self.uart.write((f"POW 0\n").encode("ascii"))
        sleep(0.1)
        self.uart.read()

class BrightnessLightDriver(BasicLightDriver):
    def __init__(self, uart):
        super().__init__(uart=uart)

    def brightness(self, value):
        dim_value = int((value / 255) * 100)
        #print(f"BrightnessLightDriver: brightness {value} {dim_value}%")
        self.uart.write((f"DIM {dim_value}\n").encode("ascii"))
        sleep(0.1)
        self.uart.read()