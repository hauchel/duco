This is work in progress.
# Overview
Instead of the huge power-consuming Arduino MiniPros, cute ATtiny85 are used for calculating the hashes.
Challenge is the missing I2C hardware, the 8 kB flash and 512 B RAM. But this still is an Arduino.  It is run with 16 MHz internal PLL, so no additional components required. Hashrate is - like MiniPro - about 195 H/s. 

Due to the low RAM those limitations currently exist:
 - difficulty not sent, fixed to 10, makes no difference
 - ducoID not used, provided by master

The I2C address tells the other programs if it's a tiny, I2C <=49 are MiniPros, 50+ attiny85.

The subsequent information is for mature readers only,  there is no support for this approach.

# Software

## SpenceKonde Core

As core used https://github.com/SpenceKonde/ATTinyCore

Using Board Manager install http://drazzy.com/package_drazzy.com_index.json
  **ATTinyCore V 1.5.2**

## Installation ATtiny
Install https://github.com/SpenceKonde/ATTinyCore

**Board** Attiny25/45/85 no bootloader

**Chip** ATtiny85

Information below depends on the fuse settings, i use
**Clock source** 16 MHz PLL


All files and directory sha1 of duino85 from https://github.com/hauchel/yaum/duino85
are required.

Connect programmer

For each tiny:

run .bat to set fuses

Compile and Flash duino85.ino

The I2 Address is in EEPROM 0 , if not provided 50 is used. It must be between 50 and 99
use **ti2ct**  to set it or avrdude Terminal  `write eeprom 0 52`

## Installation ESP
please refer to https://github.com/hauchel/duco
I'm using this config file:

    Rig 24
    51 I2C 51 AVR tiny85 (DUCO-S1A) v0.01
    53 I2C 53 AVR tiny85 (DUCO-S1A) v0.01
    54 I2C 54 AVR tiny85 (DUCO-S1A) v0.01
    55 I2C 55 AVR tiny85 (DUCO-S1A) v0.01


## I2C 

The core provides its own Wire.h, the RX/TX buffer size is 16 (good for RAM), but 32 are used for MiniPro.
See comments in Wire.h, ATtiny85 uses  USIWire.h/USIWire.cpp
USI_TWI_Slave.h defines:

    extern uint8_t TWI_Buffer[];
    #define TWI_RX_BUFFER_SIZE (16)     
    #define TWI_TX_BUFFER_SIZE (16)
    #define TWI_BUFFER_SIZE (TWI_RX_BUFFER_SIZE + TWI_TX_BUFFER_SIZE) 

Wire.h :

    extern const uint8_t WIRE_BUFFER_LENGTH;
    #define BUFFER_LENGTH (WIRE_BUFFER_LENGTH)

Changes here make things very difficult, so different commands for MiniPro and ATtiny85 are used. Also learned the hard way that here I2C contents must be read in receiveEvent else they are lost. 
While MiniPro I2C is very stable, no issues within 24 hour operation, the ATtiny sometimes fail, currently no idea wether it's hardware, software or the moon. An example for error on target 51, usually a retry helps

    51 i2c req Exc: [Errno 19] ENODEV
    51 ERR Sta Komisch? K			    <- query failed
    53 ela: 1413 res: 276 rat: 195
    51 ela: 1844 res: 356 rat: 193  	<- query ok
    51 PER getRes took 2601
    51 GOOD took 4915
    51 PER getJob took 3405

Still experimenting with different I2C pullups, currently 4K7 are used.
    
    

## Programmer

To use an Arduino as In System Programmer (ISP),  while programming these connections should exist. 
The programmers SS controls the RST of its victim, all others are connected 1:1. 
||Programmer       |Programmed  ||                    
|---|---|---|---
|    GND |	brn|		brn| 	GND|
|				|		|blue	|RST|
 |   VCC 	|red	|	red	|	VCC|	
|    SCK 	|orng|		orng|	SCK|
 |   MISO	|yell	|	yell|	MISO	|
  |  MOSI	|grn	|	grn |	MOSI|
   | SS  	|blue|

There is a standard ISP connector 2*3 which is also available on many others like Nano or Uno, top view:
|   |  |  |
|---|---|---|---			
|red |	grn	|	brn|
|	VCC|  	MOSI| 	GND|
|	MISO|	SCK	|	RST
|	yell	|blue|	?

And last but not least i use my own connector very well fitted for ATtiny x5. This is also the connection on the bus. top view:

 |1 |2  |3| 4|5|6|  
|---|---|---|---|---|---	
|RST |VCC |	SCK|MISO|	MOSI|	GND|
|(pin) |8|	 7|	 6|	 5|
|	|VCC|PB2|PB1|PB0|		
|	|RST|PB3|PB4|GND|
|(pin)  | 1	| 2| 3|	 4|
				 
During operation those are used:

PB3 is a LED vs GND (+R of course)

PB4 is used for debug output (CH0)

SDA is PB0 green

SCL is pB2 blue

As all MISOs are connected on the bus, it must not be used for output(!).
An Saleae LA is connected for debugging, trigger on SCL going low.

Instead of Arduino as programmer there are many others available. Helpful to have one (like the DIAMEX AVR) which can be switched to 3.3V so it can stay connected to the ESP.

## avrdude
The software to flash is avrdude, with the Arduino IDE it is usually installed in 
    \Program Files (x86)\Arduino\hardware\tools\avr\bin
The parameters passed by the IDE can be seen when uploading in the Arduino IDE, for me it looks like

    C:\Users\xyz\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino18/bin/avrdude 
    -CC:\Users\xyz\AppData\Local\Arduino15\packages\ATTinyCore\hardware\avr\1.5.2/avrdude.conf
    -v -pattiny85 -cstk500v2 -PCOM10

This is not really handy, so  use a .bat like this:

    set dude=C:\Users\xyz\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino18/bin/avrdude
    set conf=-CC:\Users\xyz\AppData\Local\Arduino15\packages\ATTinyCore\hardware\avr\1.5.2/avrdude.conf
    %dude% %conf% -v -pattiny85 -cstk500v2 -PCOM10 -t
    pause
This opens avrdude in Terminal mode, possible commands see to avrdude.pdf, most important:

     dump eeprom 0 3
     write eeprom 0 52

 There are  bat's,  `duT.bat`  to enter Terminal mode, `duFuse.bat` to update the fuses 

This shows the fuses, use fuse calculator e.g. https://www.engbedded.com/fusecalc/  
Factory defaults are `Fuses OK (E:FF, H:DF, L:62)`

This means it runs with 1 MHz only, therefore the -B100 was required). To change to 8MHz and to preserve EEPROM content append the line below:

    -U lfuse:w:0xe2:m -U hfuse:w:0xd7:m -U efuse:w:0xff:m
      Fuses OK (E:FF, H:D7, L:E2)

To additionally set brownout to 4.5 V (very  recommended) use `

    -U lfuse:w:0xe2:m  -U hfuse:w:0xd4:m  -U efuse:w:0xff:m
    Fuses OK (E:FF, H:D4, L:E2)

To additionally set clock frequency to 16 MHz (very, very  recommended) use `

    -U lfuse:w:0xf1:m  -U hfuse:w:0xd4:m  -U efuse:w:0xff:m
    Fuses OK (E:FF, H:D4, L:F1)

  And thats the content   






## I2C Interface 
Commands
|char|Meaning       |Example       |Action by Slave                    
|---|---|---|---
|A   |clear flags        |A              |sets runS to I                     |
|D   |set difficulty     |D06|not used                                          |
|E   |provide exec time|E     |sets *                             |
|H   |hashme             |H              |start hashing                      |
|I   |provide ID         |I              |not used                                   |
|L   |lastblockhash 0:14 |L4e329de23..             |store         |
|M   |lastblockhash 14:28|M4e329de23..             |store         |
|N   |lastblockhash 28:40 |N4e329de23..             |store         |
|O   |newblockhash 0:14  |O4e329de23..             |store  |
|P   |newblockhash 14:28  |P4e329de23..             |store  |
|Q   |newblockhash 28:40  |Q4e329de23..             |store start hashing  |
|R   |*  provide Result  |R            |                                   |
|S   |*  provide Status  |S                        |runS (runR slCmd)    |
|V   |set twi Adr        |V8                       |set new Addres and restart |


## Sha1

The current construction uses strings which is very unfortunate as it allocates space on the heap which we don't have. 
 A description of the algorithm is available at https://daknuett.github.io/cryptosuite2/usage_arduino.html#id2
 Basic idea: send lastblock by sha1.print with the number attached, example:

    Sha1.print(lastblock);Sha1.print(ducos1res);
      01234567890123x56789o1234567x90123456789
     >c96e5571a211e356857e0db05e470f559ff012c80<     0
     >c96e5571a211e356857e0db05e470f559ff012c850<   50 
     >c96e5571a211e356857e0db05e470f559ff012c8100< 100

  Then check the encrypted result comparing  20 ( SHA1_HASH_LEN defined in constants.h) bytes with the newblock (jj is prepared by compressing the 40  to 20):

    uint8_t *hash_bytes = Sha1.result();
    if (memcmp(hash_bytes, jj, SHA1_HASH_LEN * sizeof(char)) == 0)  


Changes in config.h as recommended saves 84 bytes of RAM

    #define SHA256_DISABLED
    #undef  SHA256_ENABLE_HMAC
    #undef  SHA1_ENABLE_HMAC
    #define SHA256_DISABLE_WRAPPER

Looks good: 

    Sketch uses 6312 bytes (77%) of program storage space. Maximum is 8192 bytes.
    Global variables use 302 bytes (58%) of dynamic memory,
    leaving 210 bytes for local variables. Maximum is 512 bytes.
    




