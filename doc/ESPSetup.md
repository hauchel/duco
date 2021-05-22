## Hardware

Most important  stable voltage supply 3.3 V

On Breakout board  ESP 12-F i used these wire colors:

        pink    RST					TXD		white to RX
            	ADC					RXD		yello to TX
            	CH_PC			SCL	GPIO5 	blue
            	GPIO16			SDA	GPIO4	green 
            	GPIO14				GPIO0	grey
		        GPIO12				GPIO2	pup VCC
		    	GPIO13				GPIO15	pup GND
    	red     VCC			        GND		black


For RST and GPIO0 add a 10k Pullup to VCC and button to GND.
**Reset:**  press pink .
**Enter programming mode** : hold grey, press pink,  release pink,  release grey


## Out of the Box
Native baud 74880,  Then 115400
Modem Mode very different Software depending on version
Use espSer.py for first Steps


## MicroPython Setup

Install according to https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html

download bin
pip install esptool
With   connected to Com3 PC Flash bin:
Set to programming mode, then:
        
    python -m esptool --port com3 erase_flash
    ...
    esptool.py v3.0
    Serial port com3
    Chip is ESP8266EX
    Crystal is 26MHz
    Erasing flash (this may take a while)...
    Chip erase completed successfully in 15.5s
    Hard resetting via RTS pin...

    python -m esptool --port com3 --baud 460800 write_flash --flash_size=detect 0 esp8266-20210418-v1.15.bin
    ...
    Auto-detected Flash size: 4MB
    Wrote 632632 bytes (415633 compressed) at 0x00000000 in 17.2 seconds (effective 294.2 kbit/s)...
      

Connect via Serial with 115200 (e.g. TeraTerm):

    c∟♦2B☼lÂPerforming initial setup<
    >#5 ets_task(4020eea0, 29, 3fff9030, 10)<
    >MicroPython v1.15 on 2021-04-18; ESP module with ESP8266
    Type "help()" for more information.

In boot.py modify WLAN credentials, then upload  using ampy on comx (after leaving TeraTerm). If you are happy with the WebREPL password 'p' also upload webrepl_cfg.py: 

    ampy --port COM3 put boot.py boot.py
    ampy --port COM3 put webrepl_cfg.py webrepl_cfg.py

Open TeraTerm again and press CR

    >>

Press Control-D:

    MPY: soft reboot
    Boot Duco
    boot Exception no module named 'i2ct'
    WebREPL daemon started on ws://192.168.178.39:8266
    Started webrepl in normal mode
    MicroPython v1.15 on 2021-04-18; ESP module with ESP8266
    Type "help()" for more information.

The Exception message is ok as i2ct is not installed yet. The IP of the ESP is provided by the router and varies.  Using this IP open webrepl (i installed it in c:\esp\webrepl):

    file:///C:/esp/webrepl/webrepl.html#192.168.178.39:8266/

then press button Connect and provide the password p

## ampy

    python -m pip install adafruit-ampy
    ampy --port COM3 --baud 115200 ls
    ampy --port COM3 put boot.py boot.py

 
## webrepl

    >>> import webrepl_setup
    New password (4-9 chars): microp
    PY: soft reboot

    WebREPL daemon started on ws://192.168.4.1:8266 
    WebREPL daemon started on ws://192.168.178.41:8266


## Wifi
The password for the WiFi is micropythoN (note the upper-case N). Its IP address will be 192.168.4.1 once you connect to its network.
 This is not used and intentionally disabled

 From windows need to connect via wifi, then open putty 









