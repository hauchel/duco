This documentation is work in progress. Please see doc folder for more information.

# Overview

I'm running  rigs  with one  ESP8266 12F and n Arduino Mini Pros connected by I2C. ESP runs a MicroPython program which communicates with the server via LAN and the MiniPros via I2C. For each Arduino one connection is made to the server. Technically it's possible to have more MiniPros per ESP, but the problem is the time it takes to transfer from / to the server. The ESP can only work on one server connection at a time, real computers like Raspis can do something else while the server is busy. 

# Hardware
A rig consists of 3 MiniPro and one ESP.  Each ESP connects via WiFi to the router (e.g. FritzBox)  and gets an IP-address assigned . A MiniPro stores its I2C adress in its EEPROM so it does not forget it when brainwashed . It must be unique per rig, but its clearer  to have different adresses for each MiniPro. 

# Software

Software consists of
boot.py		boot script or use your own
webrepl_cfg.py access to ESP via webREPL Password 
i2ct.py	
duclas.py
mydu.py
Setup

# boot.py


the cluster consists of several unit
## mydu
The main program has several commands for debugging purposes,
For daily ops only 3 are needed:
s to start  reads configuration file 
l to loop 99999 
if a key is pressed it returns to the menu
x  to exit
H> x
closed
closed
closed
MicroPython v1.15 on 2021-04-18; ESP module with ESP8266
Type "help()" for more information.
to restart use 
but do not use s again as the connections still exist

drop a connection with d, can use it everytime
l to
 loop
o overview 
i statistic 

Logfile looks like this

    ===Loop  99851
    *** Targ  20 Sta  C				<- C = MiniPro completed previos calc
    ela 2863  res  476  rat 166     <- fetched values from MiniPro took 2863 ms to find 476
    SndRes took  755				<- 755 ms to send result to server
    GOOD							<- of course 
    ReqJob took  1431				<- 1431 ms to request a new job
    Hashes sent  30					<- 30 ms to send hashes to Minipro which starts calculating
    *** Targ  21 Sta  C				<- next 
    ela 2707  res  450  rat 166
    SndRes took  4520				<- oops it took 4.5 seconds to send result
    GOOD
    ReqJob took  3669				<- and 3.6 to fetch new job
    Hashes sent  34
    *** Targ  22 Sta  C
    ela 12  res  1  rat 83
    SndRes took  514
    GOOD
    ReqJob took  636
    Hashes sent  30                  

Average values  when the server is in a good mood:

    Target 20  Connected True
    Name >I2C 20 AVR Miner (DUCO-S1A) v2.47<
    Requests  308				<- calculated 308 hashes
    ReqWait  271532  per  882	<- average 882 ms to request job
    ReqZwi  1060  per  3		<- thereof average 3 ms to send, rest 882-3 ms waiting
    SndWait  246115  per  799	<- average 799 ms to send result
    SndZwi  117  per  0			<- thereof average 0 ms to send
    Targ Busy  611				<- 611 times checking the Minipro had not yet completed calculation

With a hash rate of 160 difficulty 5 it takes the Arduino average 1500 ms maximum 3000 ms to calculate.  So for me it does not make sense to have more than 3 Arduinos per ESP as they  often wait for jobs but reduce the kolka rating.

Every  10 seconds a performance check program queries my  balance:
Using 3 rigs (e.g. 3 ESP<and 9 Arduinos) today shortly after the restart (?)  of  the server

    values below in milliDuco
    Time            Total  ping    10 sec    minute    Duco/d
    19:47:00       49.549   902     9.136    38.267     55.10
    19:47:10       53.310    16     3.760    37.420     53.89
    19:47:20       62.226   385     8.916    38.767     55.82
    19:47:30       66.221   168     3.995    38.202     55.01
    19:47:40       74.292    16     8.071    38.479     55.41
    19:47:50       80.716   453     6.424    40.303     58.04
At 19:47:10  the time to get the balance was 16 ms.  In the previos 10 seconds the balance increased by 0.003760 Duco, in the last minute (moving average) the balance increased by 0.037420 Duco which would be 53.89 Ducos a day. Unfortunately this is not the normal. Now i get
    
    21:55:50     2854.008   149     1.786    14.837     21.37
    21:56:00     2857.239   965     3.232    14.554     20.96
    21:56:10     2858.861   138     1.622    14.410     20.75
    21:56:20     2860.974   670     2.113    14.252     20.52
    21:56:30     2865.037   461     4.063    14.761     21.26
