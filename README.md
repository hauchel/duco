This documentation is work in progress. Please see doc folder for more information.

# Overview

I'm running  rigs  with one  ESP8266 12F and n Arduino Mini Pros connected by I2C. ESP runs a MicroPython program which communicates with the server via LAN and the MiniPros via I2C. For each Arduino one connection is made to the server. Technically it's possible to have many MiniPros per ESP, but the problem is the time it takes to transfer from / to the server.  Currently having 3 MicroPros per ESP seems to be a good value.
Goal was to have a standalone-miner powered by the sun via accus.
**Disclaimer:** This approach is not suited to obtain high performance. Actually the MiniPros only work about 60% of the time, the rest is waiting for the server. 


# Hardware
A rig consists of 3 MiniPro and one ESP.  Each ESP connects via WiFi to the router (e.g. FritzBox)  and gets an IP-address assigned . A MiniPro stores its I2C adress in its EEPROM so it does not forget it when brainwashed. It must be unique per rig, but its clearer  to have different adresses for each MiniPro. 

# HMI

The human machine interface exudes the charm of the early 80s of the last century, UPN is used: possibly digits then command. Commands are only one letter, of course upper and lower case are important. A command is executed immediately, no CR required. Due to the limited ressources there is no online help available.

Communication with ESP either via Serial 115200 with a terminal program (i use TeraTerm), or via webREPL, a terminal in a browser connected via WLAN, this is part of MicroPython. 

Communication with MiniPro via I2C or Serial, both understand the same commands. As talking I2C is quite difficult, use terminal program with 38400. This is only required for flashing the MiniPro or development/debugging. 

The state of the cluster is also indicated by MiniPro LEDs, they light up when getting an instruction from the ESP or while calculating.

# Software

**Software for ESP** consists of
 -  boot.py					Boot script or use your own 
 - webrepl_cfg.py  		Access to ESP via  webREPL Password p
 -  i2ct.py	 				Class for I2C 
 - duclas.py 				Class for server 
 - mydu.py					Main program

Challenge is that for compiling the python code on ESP there must be enough free RAM available. Compiling is triggered by the first import statement, subsequent imports don't need this. Use dir() to check the compiled modules.
When mydu is running, the free RAM can be inquired, currently its about 20 k.
The MicroPython setup is described in ESPSetup

**Software for Arduino** is in folder yaum, it's the same as Revox repo (sha1 and uniqueID) except the duino.ino.

**Software for Raspi or Windows**, Python3 must be installed,  See description DucoPerf in folder doc.

 - jperf.py		show performance, actual growth of Duco balance 
 - jmin.py		show miners as seen by the server


**Other**
I change the python code on windows (Anaconda Spyder) therefore some batchfiles are used  to transfer the python from windows to ESP, like putmydu.bat:

    python webrepl_cli.py -p p mydu.py 192.168.178.%1:/mydu.py
calling it with 

    putmydu 41

    
transfers the script mydu.py to ESP with IP 192.168.178.41. 
Slightly faster than compiling and flashing ESP with Arduino IDE.

