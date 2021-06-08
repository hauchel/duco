# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#wlan.connect('FRITZ!Box 7312','30728671214167815478')
wlan.connect('NETGEAR','12345678')
hots =network.WLAN(network.AP_IF)
hots.active(False)

print ("Boot Duco")
try:
    from i2ct import i2ct
    from duclas import cserv
    from duclas import ccon
except Exception as inst:
    print ("boot Exception "+str(inst))

import webrepl
webrepl.start()
import mydu


