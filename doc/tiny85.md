This is work in progress.
# Overview
Instead of the huge power-consuming Arduino MiniPros, cute ATtiny85 will be used for calculating the hashes. Challenge is the missing I2C hardware, the 8 kB flash and 512 B RAM. But this still is an Arduino. The subsequent instructions are for mature readers only. There is no support for this approach.

Due to the low RAM those limitations currently exist:
 - difficulty not used, fixed to 10  
 - ducoID not used, provided by master
 - time calculation also provided by master

TWI addr must be set while beeing 


# SpenceKonde Core

https://github.com/SpenceKonde/ATTinyCore
Doc Quality good
Board Manager
http://drazzy.com/package_drazzy.com_index.json
Install  **ATTinyCore V 1.5.2**
Board Attiny25/45/85 no bootloader
Chip ATtiny85
Clock source:

## twi

Unfortunately the RX buffer size is 16 (good for RAM), but we need 32:
( 1,2,4,8,16,32,64,128 or 256 bytes are allowed buffer sizes for TX and RX):
See comments in Wire.h, ATtiny85 uses  USIWire.h/USIWire.cpp
USI_TWI_Slave.h defines:

    extern uint8_t TWI_Buffer[];
    #define TWI_RX_BUFFER_SIZE (16)     
    #define TWI_TX_BUFFER_SIZE (16)
    #define TWI_BUFFER_SIZE (TWI_RX_BUFFER_SIZE + TWI_TX_BUFFER_SIZE) 

And Wire.h 

    extern const uint8_t WIRE_BUFFER_LENGTH;
    #define BUFFER_LENGTH (WIRE_BUFFER_LENGTH)
Changes makes things more difficult so different commands for tiny85 are used:

    

## Programmer

To use an Arduino as In System Programmer (ISP),  while programming these connections should exist. The programmers SS controls the RST of its victim, all others are connected 1:1. 

    Programmer			programmed
    Mini-Pro			Mini Pro 
    GND 	brn		brn 	GND
					blue	RST
    VCC 	red		red		VCC	
    SCK 	orng	orng	SCK
    MISO	yell	yell	MISO	
    MOSI	grn		grn		MOSI
    SS  	blue

There is a standard ISP connector 2*3 which is also available on many others like Nano or Uno, top view:

			red		grn		brn
			VCC  	MOSI 	GND
			MISO	SCK		RST
			yell	blue	?

And last but not least i use my own connector very well fitted for ATtiny x5, 
top view:

		RST		VCC		SCK		MISO	MOSI	GND
				 8		 7		 6		 5
				VCC		PB2		PB1		PB0		
				RST		PB3		PB4		GND
				 1		 2		 3		 4
				 
An Saleae LA is connected for debugging, trigger on SCL going low:

				    SCL				SDA
    RST		VCC		SCK		MISO	MOSI	GND
				    CH2		CH4		CH6		GND
         
During operation those are used:
Led is PB3 vs Gnd
SDA is PB0 green
SCL is pB2 blue
MISO PB1 is used for debug output

Instead of Arduino as programmer there are many others available. Helpful to have one (like the DIAMEX AVR) which can be switched to 3.3V so it can stay connected to the ESP.

## avrdude
The software to flash is avrdude, with the Arduino IDE it is usually installed in 
    \Program Files (x86)\Arduino\hardware\tools\avr\bin
The parameters passed by the IDE can be seen when uploading in the Arduino IDE, for me it looks like

    C:\Users\hh\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino18/bin/avrdude 
    -CC:\Users\hh\AppData\Local\Arduino15\packages\ATTinyCore\hardware\avr\1.5.2/avrdude.conf
    -v -pattiny85 -cstk500v2 -PCOM10
    
This shows the fuses, use fuse calculator to interpret

     Fuses OK (E:FF, H:DF, L:62)

This means it runs with 1 MHz only, therefore the -B100 was required). To change to 8MHz append the line below:

    -U lfuse:w:0xe2:m -U hfuse:w:0xdf:m -U efuse:w:0xff:m

     Fuses OK (E:FF, H:DF, L:E2)

There are 2 bat's,  `duT.bat`  to enter Terminal mode, `duFuse.bat` to update the fuses, the paths must be changed if required.

## Installation
install as described

Commands
|char|Meaning       |Example       |Action by Slave                    
|---|---|---|---
|A   |clear flags        |A              |sets runS to I                     |
|D   |set difficulty     |D06|not used                                          |
|E   |provide exec time|not in ver c     |sets *                             |
|H   |hashme             |H              |start hashing                      |
|I   |provide ID         |I              |not used                                   |
|L   |lastblockhash 0:20 |L4e329de23..             |store         |
|M   |lastblockhash 20:40|M4e329de23..             |store         |
|N   |newblockhash 0:20  |N4e329de23..             |store         |
|O   |newblockhash 0:40  |O4e329de23..             |store start hashing  |
|R   |*  provide Result  |not in ver c             |                                   |
|S   |*  provide Status  |S                        |runS (runR slCmd)                  |
|V   |set twi Adr        |V8                       |set new Addres and reboot          |




