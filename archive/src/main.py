from os import stat
from time import sleep
from machine import reset

print("Starting ... wait 5 sec")
sleep(5)

try:
    if stat("/ota.lck"):
        print("Starting in OTA mode")
        import ota
        sleep(3)
        reset()
except KeyboardInterrupt:
    raise
except:
    pass

try:
    print("Starting main app")
    import app
except:
    print("Failed to start main app, entering to OTA mode")
    with open("/ota.lck", 'a'):
        pass
    sleep(3)
    reset()