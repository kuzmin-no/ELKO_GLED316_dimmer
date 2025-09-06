# Making ELKO 316 GLED dimmer smart (again)

NB! The previous Micropython version of application moved to [Archive](./archive) folder.

[ELKO RS16/316 GLED dimmer](https://www.elko.no/produkter/14-brytere-og-dimmere/dimmere/elko-rs/polarhvit/rs16-316-gled-dimmer-ph)
is superb two-pole dimmer with the ability to switch between leading edge (GLI) and trailing edge (GLE) dimming.
The dimmer includes an embedded `ATxmega32E5` microcontroller, with firmware that can be upgraded using an integrated micro-SD card reader.
This dimmer has several modifications; one of them, the `RF` model, includes a Zigbee module, while the `PH` modification does not.

I disassembled one of `PH` dimmers and found that if has an installation spot for Zigbee module.
Identical dimmers might have adapter boards for different modules.

- [GLED316 front](./img/GLED316_front.jpg)
- [GLED316 back](./img/GLED316_back.jpg)
- [GLED316 mainboard front](./img/GLED316_mainboard_front.jpg)
- [GLED316 mainboard back](./img/GLED316_mainboard_back.jpg)
- [GLED316 sdcard adapter top](./img/GLED316_sdcard_adapter1.jpg)
- [GLED316 sdcard adapter bottom](./img/GLED316_sdcard_adapter2.jpg)

On the `SD-card` adapter board, there are labels marked `RX` and `TX`, which most likely indicate the UART link between the microcontroller and the Zigbee board.
According to another label, the voltage level is +3 volts, so it can be directly connected to a UART-USB adapter to check the output.

After connecting, we can discover that the dimmer communicate using a standard serial protocol with a speed of `115200` bps and `8N1` configuration.
The dimmer sends a text string when its status changes (e.g., switching on/off or changing the dimming level).
It also accepts commands and changes its status accordingly. Below is a list of commands and examples of responses:

| Command | Description                                          | Example command | Example answer |
|---------|------------------------------------------------------|-----------------|----------------|
| STA     | Status                                               | STA             | OK 0,100       |
| POW N   | Set power state, where N can be 0 (off) or 1 (on)    | POW 1           | OK 1,100       |
| DIM Y   | Set dimmer state, where Y can be from 0 to 255 (max) | DIM 50          | OK 1,50        |
| VER     | Firmware version                                     | VER             | 0.9.36         |

The response `OK` has to arguments: the first one indicates the power state, and the second one indicates the dimmer state.
Another possible response is `ERROR XX,Y`. Examples of such outputs are as follows:

    ERROR 99,2 - command not found
    ERROR 00,3 - value is out of range
    ERROR 00,1 - value is incorrect

- [Link to dimmer's firmware](./firmware)

According to the documentation, you can set the dimmer to special modes by pressing the `push button` and the dimmer knob.
In these cases, the dimmer sends the following commands to the Zigbee module:

| Command | Description                   | How to enter in this mode                                                                                       |
|---------|-------------------------------|-----------------------------------------------------------------------------------------------------------------|
| RES     | Reset, start firmware upgrade | Press small "push button" and dimmer knob at the same time for 1-3 sec                                          |
| LRN     | Zigbee pairing mode           | Press small "push button" for apporx 10 seconds, when LED flashes release "push button" and press dimmer knob.  |

It is likely that one of the Zigbee modules used is the [Telegesis ETRX357](https://eu.mouser.com/datasheet/2/368/TG_PM_0511_ETRX358x_LRS-3083307.pdf),
which costs approximately 26 EUR. Although I do not have this module, but we can use any [ESPHome](https://esphome.io/index.html) compatible microcontroller.
I have tested Raspberry Pi Pico W and ESP-12F. It is easy to develop and debug on Raspberry Pi Pico W, but ESP-12F module has almost
the same dimensions as the original Zigbee modules, and ESP platform supports captive portal.

- [Connection diagram](./img/Connection_diagram.png)
- [STL files for Raspberry Pi Pico case](./stl)
- [GLED316 smartdim with Raspberry Pi Pico W top](./img/GLED316_smartdim1.png)
- [GLED316 smartdim with Raspberry Pi Pico W side](./img/GLED316_smartdim2.png)

There are examples of ESPhome configuration for ELKO dimmer as:
- [Switch](./ESPhome/ELKO_switch.yaml)
- [Light Binary](./ESPhome/ELKO_light-binary.yaml)
- [Light Monochromatic](./ESPhome/ELKO_light-monochromatic.yaml)

These examples also implement RES and LRN commands mentioned above: 
- RES - Restarts the ESPHome device.
- LRN - Start the  ESPHome device in AP mode for adjust Wi-Fi configuration or upload an OTA update.
When in AP mode, the ESPHome device will automatically restart into standard mode after 10 minutes,
or you can use the RES command to restart it manually.