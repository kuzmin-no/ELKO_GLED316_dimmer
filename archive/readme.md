# Making ELKO 316 GLED dimmer smart (again) - Archive version

NB! This is an archived version of the application on MicroPython. It turned out to use quite a lot of RAM and may become unstable.
It is recommended to use ESPHome if you have a Home Assistant deployment.

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
        "device_name": "name_of_device",
        "device_type": "switch or dimmer", 
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
        "device_name": "test_device",
        "device_type": "switch",
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

The MQTT service supports discovery; however, you can also define the following topics manually if needed. For example, with the MQTT device name `kitchen_benk`:

    homeassistant/light/kitchen_benk/set
    homeassistant/light/kitchen_benk/state

The values must be in JSON format. For instance:

```json
{"state": "OFF"}

{"state": "ON", "brightness": 100}
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
        "onValue": "{\"state\": \"ON\"}",
        "offValue": "{\"state\": \"OFF\"}",
        "manufacturer": "ELKO",
        "model": "316 GLED",
        "firmwareRevision": "0.9.36"
    },
    "accessory": "mqttthing"
```
