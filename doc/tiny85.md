This is work in progress.
# Overview
Instead of the huge power-consuming Arduino MiniPros,  cute ATtiny85 will be used for calculating the hashes. Challenge is the missing I2C hardware, the 8 kB flash and 512 B RAM. But this still is an Arduino.

# Cores

## SpenceKonde

https://github.com/SpenceKonde/ATTinyCore
3 month ago
all tinies
Doc Quality good
Board Manager
http://drazzy.com/package_drazzy.com_index.json
Install  **ATTinyCore V 1.5.2**
Board Attiny25/45/85 no bootloader
also check 

## damellis

https://github.com/damellis/attiny
5 years ago
supports 25,45,85
http://highlowtech.org/?p=1695
Board Manager


## TWI
```
#include <TinyWireS.h>

https://github.com/watterott/Arduino-Libs/tree/master/TinyWire
https://github.com/rambo/TinyWire
https://codebender.cc/example/TinyWireS/attiny85_i2c_slave#attiny85_i2c_slave.ino
```
 

## Preliminaries

     program storage space. Maximum is 32256 bytes.
     dynamic memory	Maximum is 2048 bytes.
     required free???
           
    original for 328:
     8508 bytes (26%) of program storage space. 
     539 bytes (26%) of dynamic memory, leaving 1509 bytes for local variables. 

 Strip everything less sha1 and compile :     

**Mega328**
 
      5076 bytes (15%) of program storage space. 
       58 bytes (2%)of dynamic memory

 **ATTinyCore V 1.5.2**
 
     4672 bytes (57%) of program storage space.
      58 bytes (11%) of dynamic memory
 
 ** Duino for  328**
 
    11780 bytes (36%) of program storage space. 
     874 bytes (42%) of dynamic memory
	OK, at least try it


**Layout**

## Programmer

To use an Arduino as In System Programmer (ISP),  while programming these connections should exist. The programmers SS controls the RST of its victim., all others are connected 1:1. This can be used for burning boodloaders

    Programmer				programmed
    Mini-Pro				Mini Pro 
    GND		brn		brn 	GND
					blue	RST
    VCC		red		red		VCC	
    SCK		orng	orng	SCK
    MISO	yell	yell	MISO	
    MOSI	grn		grn		MOSI
    SS		blue

There is a standard ISP connector 2*3 which is also available on many others like Nano or Uno, top view:

			red		grn		brn
			VCC  	MOSI 	GND
			MISO	SCK		RST
			yell	orng	blue

And last but not least i use my own connector very well fitted for ATtiny x5, 
Top view:

		RST		VCC		SCK		MISO	MOSI	GND
				 8		 7		 6		 5
				VCC		PB2		PB1		PB0		
				RST		PB3		PB4		GND
				 1		 2		 3		 4

Instad of Arduino as programmer popular is USBASP or 

The software to flash is avrdude, with the Arduino IDE it is usually installed in 
    \Program Files (x86)\Arduino\hardware\tools\avr\bin
The parameters passed by the IDE can be found in ?
 







