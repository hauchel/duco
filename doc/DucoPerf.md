## Overview

In Duino-Coin the hashrates are an important issue. The values shown somehow yield in Ducos, but it is not clear how, because it depends on many parameters.  But Performance means Ducos per day and that's what really counts.

To improve the performance of my humble rigs i was interested in the actual increase of my balance while running different number of miners. 

The publicly available data from the  REST API (https://github.com/dansinclair25/duco-rest-api)  is collected and shown on the console by two python scripts.
 
It turned out that these scripts are helpful to compare the performance of other users miners.

## Installation

 python3 is required, tested on win10 and raspi

easy way:

    git clone https://github.com/hauchel/duco


But these files are needed only:

    jperf.py
    jmin.py
    kbhit.py


In the directory where the .py are located make a directory named logs, here the results are stored

    pi@r1:~/wrk/perf $ ls
    jmin.py  jperf.py  kbhit.py  
    pi@r1:~/wrk/perf $ mkdir logs

In the jperf.py and jlog.py modify the username to your needs. This is the default user inquired.

    username = "targon"
If you are frequently interested in certain users,   provide a  file with name privusers.py, having many users, e.g for 3 it looks like

    user=['user0','user1','user2']

for usernames capitalization matters.
    

## jperf
Invoke jperf.py, optionally a username can be provided as parameter.
After the first few lines are shown, press any key:

    pi@r1:~/wrk/perf $ python3 jperf.py
    no privusers.py, having
    user=['user0','user1','user2']
    username is  targon
    One Moment...
    Logfile logs/perf_targon_29_20.txt
    Starting Sat May 29 20:14:39 2021 with 423.575044802086
    values below in milliDuco, allow 1 minute settling time
    Time          Total   Hash Mnr    10 sec    Minute    Duco/d
    20:14:40      0.000   1614  12     0.000     0.000      0.00
    20:14:50      5.879   1614  12     5.879     5.879      8.47
    20:15:00      7.732   1559  12     1.854     7.732     11.13
    20:15:10      9.678   1639  12     1.946     9.678     13.94
    20:15:20     12.628   1568  12     2.950    12.628     18.18
    20:15:30     15.159   1639  12     2.530    15.159     21.83
    20:15:40     18.008   1568  12     2.850    18.008     25.93
    20:15:50     22.714   1636  12     4.706    16.836     24.24
    20:16:00     25.171   1636  12     2.456    17.438     25.11
    20:16:10     27.921   1600  12     2.750    18.243     26.27
    Terminated
    targon P>

When starting the script i owned 423.57... Ducos
The values shown for some columns are  milliDuco i.e. 1/1000 of a Duco.
Then each 10 seconds the REST API is inquired, the data printed and written to the logfile.

**Time** is localtime

**Total** the current difference of balance and starting value

**Hash** is the sum of all hashrates of the miners

**Mnr** is the number of miners currently running

**10 sec**  is the balance difference obtained in the last 10 seconds

**Minute** is the floating avarage of the last 6 values

**Duco/d** then shows this as  actual Ducos/day

It creates a logfile in the directory logs, name contains the username, the day of month and the hour it was started. If running several times an hour the information is appended in the log.
These commands are available

    b  Balance
    q  Query
    o  show Other users
    u  switchUser, e.g. 3u
    f  Fast mode:    tick 2 seconds
    n  Normal mode: tick 10 seconds
    x  eXit

o shows the users as provided in privusers.py, swith to this user by entering a number then u, e.g 
## jmin
Invoke jmin.py, optionally a username can be provided as parameter.
After the first few lines are shown, press any key:

    pi@r1:~/wrk/perf $ python3 jmin.py
    no privusers.py, having
    user=['user0','user1','user2']
    username is  targon
    Press any key to abort  <<<<
    keyboard only checked every second
    Logfile logs/min_targon_29_21.txt
    Starting Sat May 29 21:08:56 2021
    Tick  10
    21:09:00 Running  12                Diff      Acc/Rej      Hash      Time
     Rig 40 I2C 11 AVR Miner (DUCO-S1      6      10  R 0     148.0     1.576
     Rig 40 I2C 12 AVR Miner (DUCO-S1      6      10  R 0     104.0     1.503
     Rig 40 I2C 13 AVR Miner (DUCO-S1      6      10  R 0     120.0     2.422
     Rig 41 I2C 15 AVR Miner (DUCO-S1      6    3540  R 0     121.4     1.335
     Rig 41 I2C 16 AVR Miner (DUCO-S1      6    3505  R 0     124.0     1.665
     Rig 41 I2C 17 AVR Miner (DUCO-S1      6    3520  R 0     126.6     0.519
     Rig 42 I2C 20 AVR Miner (DUCO-S1      6    1175  R 0     140.0     1.319
     Rig 42 I2C 21 AVR Miner (DUCO-S1      6    1170  R 0     109.6     1.180
     Rig 42 I2C 22 AVR Miner (DUCO-S1      6    1255  R 0     142.6     2.478
     Rig 39 I2C 25 AVR Miner (DUCO-S1      6    1110  R 0     144.2     3.737
     Rig 39 I2C 26 AVR Miner (DUCO-S1      6    1205  R 0     122.0     1.891
     Rig 39 I2C 27 AVR Miner (DUCO-S1      6    1200  R 0     145.6     2.651
    21:09:00      Tot    1548.0                   Arduino    1548.0
    Terminated
    targon M>
At 21:09 12 miners were running . These values are shown for each miner:

The **ID** of the rig with 7 chars and the **software** with 25 chars

**Diff** the difficulty assigned

**Acc/Rej** number of accepted and rejected jobs

**Hash** the hashrate. As i don't provide the hashrate to the server, the estimated rate is shown

**Time** the time between the server sending the job and getting the result

Then the **Total** of all hashrates and the total of **Arduino** hashrates (below 200) is shown.

The values are only updated by the server in intervals of 5 , i.e. the values only change after 5 jobs are completed for a miner.

These commands are available:

    j  Json with tick n
    q  Query  tick 10
    a  sort by accepted
    h  sort by hashrate
    n  no sort
    s  sort by software
    t  sort by time
    r  toggle reverse
    o  show Other users
    u  switch to User n then query fast
    x  eXit




# Performance of the Rigs

A Job is processed in these steps:

 - Send request to the server 
 - Wait for job 
 - Process job 
 - Send result to the server 
 - Wait for verdict

These are the states used , slave states are Idle, Busy and Complete:
|Sta|Meaning|Slave|nxt |Comment                           |
|---|---------------------|-----|----|----------------------------------|
|D  |disconnected         |?    |-> C|try to connect to server          |
|C  |connected            |I    |-> R|reset  slave, send request        |
|R  |request sent         |I    |-> J|poll                              |
|J  |job received         |I    |-> K|hash to slave                     |
|K  |transferred to slave |B    |    |Wait for slave C |
|K  |transferred to slave |C    |-> W|and reset slave|
|W  |wait for send        |I    |-> E|speed limit for fast slave, then send result|
|E  |result sent          |I    |-> F|poll    |
|F  |result response Error|I    |->D |This should not occur  |
|G  |result response Good |I    |->C |                                  |

Three timestamps are recorded:

 - jobStart	when sending request, when setting state to R.
 -  getJobWait  difference to start i.e.  from R to setting to J.
 -  getResWait  difference from E to setting to C,  this is the ping time shown in the AVR_Miner.py 
 -  overall time is the difference of result received and jobStart.
 -   processing time to communicate with the slave (<40ms) and task switches. This is the difference of the sum and the overall time
 The Wait for send is required for 16 MHz lgt8fx with hashrate 230, as the server rejects any transaction with a hashrate > 200 as calculated by the server, see below.

This is shown in the output:

    26 PER getJob took 1825			<-getJobWait
    26 ela: 270 res: 51 rat: 189	<-slave elapsed 270 ms
    26 PER getRes took 266			<-getResWait
    26 GOOD took 2428				<-overall

So here we have 

    1825 ms to get job
     270 ms to calculate
     266 ms to send result
	2361 ms sum of above
	2428 ms overall time
	  67 ms processing time 

The actual calculation took 270 ms, but the job 2428 ms, i.e the arduino only earns in 1/9 of the time. This is just an extreme  example (small time to calculate and high wait time),  each job gives different values. 
These are avarages for 4 rigs with 3 Arduinos and one ESP each, just one randomly picked, others are similar for same time recorded. 

    Requests 6179
    ReqWait 3258727 per 527
    SndWait 1551892 per 251
    Ela 9578942 Res 1850469 Avg 193
    Targ Busy 687829 per 111

     527 ms to get job
    1550 ms to calculate (Ela/Requests)
     251 ms to send result
      70 ms est. processing time
	2398 ms sum 
	 
The overall time is not recorded, so assume 70 ms processing time.
Here we have about 64% (1550/2398) calculation time which is much better for my wallet.
Targ Busy 111 means in slave state B the master queried average 111 times per job if the slave has finished calculation.  This means an average loop time of roughly estimated 14 ms (1550/111) for handling the three slaves.

There are two hashrates, one is the locally obtained, this is always about 190-195 for 16 MHz Mini Pro, depending on the result. It is measured by the Mini Pro, so a frequency deviation like 15.9 MHz  would not change the reported hashrate but the real hashrate would be smaller. 
If the hashrate is not sent, the server calculates it from the time difference between sending the job and receiving the result.  This is much lower, as it includes the time to send the result:
Just a random example:

    12:38:50 Running  12                Diff      Acc/Rej      Hash      Time
     Rig 39 I2C 25 AVR Miner (DUCO-S1      6    1985  R 0     165.6     1.645
     Rig 41 I2C 17 AVR Miner (DUCO-S1      6    5360  R 0     163.2     2.708
     Rig 41 I2C 16 AVR Miner (DUCO-S1      6    5340  R 0     159.4     2.783
     Rig 42 I2C 20 AVR Miner (DUCO-S1      6    5320  R 0     155.6     1.294
     Rig 41 I2C 15 AVR Miner (DUCO-S1      6    5360  R 0     146.4     2.747
     Rig 39 I2C 26 AVR Miner (DUCO-S1      6    2015  R 0     143.2     1.025
     Rig 42 I2C 21 AVR Miner (DUCO-S1      6    5375  R 0     142.6     3.979
     Rig 40 I2C 11 AVR Miner (DUCO-S1      6    5330  R 0     138.8     1.103
     Rig 40 I2C 13 AVR Miner (DUCO-S1      6    5335  R 0     135.0     1.707
     Rig 42 I2C 22 AVR Miner (DUCO-S1      6    5355  R 0     118.4     0.405
     Rig 39 I2C 27 AVR Miner (DUCO-S1      6    1995  R 0      85.2     0.229
     Rig 40 I2C 12 AVR Miner (DUCO-S1      6    5365  R 0      83.8     0.359
    12:38:50      Tot    1637.2                   Arduino    1637.2

 

 How to improve?
https://docs.micropython.org/en/latest/reference/speed_python.html#speed-python

 - an object is created once only and not permitted to grow in size.
 -  use `readinto()` method to read data into an existing buffer.
 - avoid floating point
 - [`memoryview`]is allocated on heap, but is a small, fixed-size object
 - `const()` declaration
 - periodically issuing `gc.collect()`
 - @micropython.native
 - @micropython.viper: def foo(self, arg: int) -> int:
 











