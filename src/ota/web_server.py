import uasyncio as asyncio
import json
from ahttpserver import HTTPResponse, HTTPServer, sendfile
from machine import reset
from time import sleep
from os import remove

app = HTTPServer()

# https://github.com/erikdelange/MicroPython-HTTP-Server/

def define_serial_port(uart):
    global serial_port
    serial_port = uart

@app.route("GET", "/")
async def root(reader, writer, request):
    response = HTTPResponse(200, "text/html", close=True)
    await response.send(writer)
    await sendfile(writer, "/ota/index.html")
    await writer.drain()

@app.route("GET", "/hotspot-detect.html")
async def regirect(reader, writer, request):
    headers = { 'Location': '/' }
    response = HTTPResponse(302, "text/html", close=True, header=headers)
    await response.send(writer)
    await writer.drain()

@app.route("GET", "/api/power_on")
async def power_on(reader, writer, request):
    """ Power on """
    serial_port.pow(1)
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": "Power is ON" }))
    await writer.drain()

@app.route("GET", "/api/power_off")
async def power_off(reader, writer, request):
    """ Power off """
    serial_port.pow(0)
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": "Power is OFF" }))
    await writer.drain()

@app.route("GET", "/api/status")
async def status(reader, writer, request):
    """ Dimmer status """
    power_status = serial_port.sta()
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": power_status }))
    await writer.drain()

@app.route("GET", "/api/dimmer")
async def dimmer(reader, writer, request):
    """ Set dimmer value """
    if 'dim' in request.parameters and request.parameters['dim'].isdigit():
        dim = int(request.parameters['dim'])
        if  0 <= dim <= 100:
            serial_port.dim(dim)
            await asyncio.sleep_ms(100)
    power_status = serial_port.sta()
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": power_status }))
    await writer.drain()

@app.route("GET", "/api/config")
async def config(reader, writer, request):
    """ Show config.json file """
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    await writer.drain()
    await sendfile(writer, "/app/config.json")

@app.route("GET", "/api/save_config")
async def save_config(reader, writer, request):
    """ Save config file following a HTTP PUT request """
    filename = '/app/config.json'
    with open(filename, 'w') as fp:
        json.dump(request.parameters, fp)
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": "Configuration is saved" }))
    await writer.drain()

@app.route("GET", "/api/restart_in_main_app")
async def restart_in_main_app(reader, writer, request):
    """ Delete ota.lck and restart """
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": "Rebooting in main app" }))
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    remove('/ota.lck')
    sleep(2)
    reset()

@app.route("GET", "/api/restart")
async def restart(reader, writer, request):
    """ Restart """
    response = HTTPResponse(200, "application/json", close=True)
    await response.send(writer)
    writer.write(json.dumps({ "state": "Restarting" }))
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    sleep(2)
    reset()