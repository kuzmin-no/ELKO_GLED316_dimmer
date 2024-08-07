# Making ELKO 316 GLED dimmer smart (again)

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
which costs approximately 26 EUR. Although I do not have this module, I do have a Raspberry Pi Pico W.
Therefore, we can use the Pico W with WiFi and MQTT as an alternative to Zigbee.

- [Connection diagram](./img/Connection_diagram.png)
- [STL files for Raspberry Pi Pico case](./stl)
- [GLED316 smartdim with Raspberry Pi Pico W top](./img/GLED316_smartdim1.png)
- [GLED316 smartdim with Raspberry Pi Pico W side](./img/GLED316_smartdim2.png)

I have uploaded an [example](./src/) of application that can be loaded onto the Raspberry Pi Pico W with [MicroPython](https://micropython.org/download/RPI_PICO_W/).
The application consists of two parts:
- [Folders structure](./img/Folders_structure.png)
- `/app` folder, which contains the main application.
- `/ota` folder, which includes services and utilities that may assist with upgrading and troubleshooting the application.

When the main application starts and the configuration file is absent, it creates a `/ota.lck` file and restarts in OTA mode.
In OTA mode it starts a wireless access point with the SSID: `RPI_Pico` and PSK key: `PASSWORD`.
When connected to this wireless access point, you can access the Raspberry Pi Pico at the IP address `192.168.4.1`.
The following service are available:

- **Captive Portal DNS Server**: Resolves all FQDNs to IP 192.168.4.1.
- **Web Server**: Accessible on standard HTTP port TCP/80, used to configure the main application and manage or troubleshoot the dimmer.
- **Telnet Service**: Accessible on standard port TCP/23, used to manage or troubleshoot the dimmer, restart, and change the boot mode.
- **FTP Service**: Accessible on standard port TCP/21, used to manually update or patch the main application.

The following MicroPython examples and projects were used:
- The main app is adapted from Renaud Guillon [repository](https://github.com/rguillon/hatank)
- The captive portal DNS server is sourced from Patrick McAndrew's [repository](https://github.com/urg/micropython-captive-dns-server)
- The web server is derived from Erik de Lange's [repository](https://github.com/erikdelange/MicroPython-HTTP-Server)
- The FTP server is based on David Horton's [repository](https://github.com/DavesCodeMusings/ftpdlite)

Commands implemented for `telnet` service:

    STA - displays the status of power and dimmer. All arguments will be ignored.
    POW X - sets power state, X values can be 0 (off) or 1 (on). The command without argumnets is equivalent to STA command.
    DIM Y - sets dimmer state, Y values can be in the range from 0 to 100. The command without argumnets is equivalent to STA command.
    VER - displays the firmware version
    BYE - closes telnet session
    APP - deletes ota.lck file and restarts in main app

The web service allows for creating a configuration file and managing the dimmer via API.
Below is a screenshot of the web interface:

- [Web interface](./img/Web_service.png)

Here is a list of implemented APIs. All requests must use the GET method and provide parameters via the query string:

```
/api/power_on   - power on dimmer
/api/power_off  - power off dimmer
/api/status     - provide status
/api/dimmer     - set dimmer value, via parameter "dim"
/api/config     - show content of /app/config.json file
/api/save_config         - save parameters to /app/config.json file
/api/restart_in_main_app - restart device in main application
/api/restart             - restart device
```

The FTP service (FTPdlite) has been tested with Linux Midnight Commander; however, it may be unstable.
If issues arise, it is recommended to restart the device using the web or telnet service and try again.
The username and password for FTP access: `ftpadmin:ftpadmin`

Below is an example of the /app/config.json file. You can create it manually and remove the `/ota.lck` file to start device in main application mode:

```json
    {
        "server": "IP address of MQTT server",
        "user": "Username to accessing MQTT server",
        "password": "Password to accessing MQTT server",
        "ssid": "WLAN SSID to connecting in main application mode",
        "wifi_pw": "WLAN PSK to connecting in main application mode"
    }
```

Here are the default values in the configuration structure and other possible parameters:

```python
    config = {
        "client_id": hexlify(unique_id()),
        "server": None,
        "port": 0,
        "user": "",
        "password": "",
        "keepalive": 60,
        "ping_interval": 0,
        "ssl": False,
        "ssl_params": {},
        "response_time": 10,
        "clean_init": True,
        "clean": True,
        "max_repubs": 4,
        "will": None,
        "subs_cb": lambda *_: None,
        "wifi_coro": eliza,
        "connect_coro": eliza,
        "ssid": None,
        "wifi_pw": None,
        "queue_len": 0,
        "gateway": False,
    }
```

When running the main application, you can restart the device or enter in OTA mode by pressing the respective button/knob sequence,
as described for the RES and LRN commands. The RES command will restart the device, while the LRN command will restart the device in OTA mode.
This functionality is useful when the dimmer is already installed in place, and accessing the Raspberry Pi Pico USB port is difficult.

The main application is designed to manage a single dimmer.
Currently, the type and MQTT name of the device are hardcoded in the file `/app/__init__.py`, so you will need to edit this file accordingly.


Below is an example of how to change only the power state:

```python
light_mqtt = ha_mqtt_light.HaMqttBasicLight(name="bad_lys", light=BasicLightDriver(uart), pow_status=pow_status)

try:
    while True:
        asyncio.run(main())
        if uart.any() > 0:
            (pow, dim) = read_uart()
            pow_status = "ON" if pow == 1 else "OFF"
            print(f"Status change from dimmer - power: {pow_status} dimmer: {int((dim / 255) * 100)}%")
            if light_mqtt.current_state['state'] != pow_status:
                light_mqtt.current_state['state'] = pow_status
                asyncio.run(update())
```

Here is an example of how to change both the power state and dimming:

```python
light_mqtt = ha_mqtt_light.HaMqttBasicLight(name="kitchen_benk", light=BasicLightDriver(uart), pow_status=pow_status, dim_status=dim)

try:
    while True:
        asyncio.run(main())
        if uart.any() > 0:
            (pow, dim) = read_uart()
            pow_status = "ON" if pow == 1 else "OFF"
            print(f"Status change from dimmer - power: {pow_status} dimmer: {int((dim / 255) * 100)}%")
            if (light_mqtt.current_state['state'] != pow_status) or (light_mqtt.current_state['brightness'] != dim):
                light_mqtt.current_state['state'] = pow_status
                ight_mqtt.current_state['brightness'] = dim
                asyncio.run(update())
```

The MQTT service supports discovery; however, you can also define the following topics manually if needed. For example, with the MQTT device name `kitchen_benk`:

    homeassistant/light/kitchen_benk/set
    homeassistant/light/kitchen_benk/state

The values must be in JSON format. For instance:

```json
{ "state": "OFF" }

{ "state": "ON", "brightness": 100 }
```

The integration with Home Assistant is straightforward.  Please refer to this guide for [detailed instructions](https://www.home-assistant.io/integrations/mqtt/).

Below is an example configuration for [Homebridge Mqttthing](https://github.com/arachnetech/homebridge-mqttthing#readme):

```json
    {
        "type": "lightbulb-OnOff",
        "name": "Kjøkkenbenk Lys",
        "url": "mqtt://192.168.1.111:1883",
        "username": "mqtt",
        "password": "mqttPa$$w0rd",
        "topics": {
            "getOn": "homeassistant/light/kitchen_benk/state",
            "setOn": "homeassistant/light/kitchen_benk/set"
        },
        "onValue": "{ \"state\": \"ON\" }",
        "offValue": "{ \"state\": \"OFF\" }",
        "manufacturer": "ELKO",
        "model": "316 GLED",
        "firmwareRevision": "0.9.36"
        },
        "accessory": "mqttthing"
    }
```
