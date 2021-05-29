
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
Targ Busy 111 means in slave state B the master queried average 111 times per job if the slave has finished calculation.  This means an average loop time of roughly estimated 14ms (1550/111) for handling the three slaves.

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
 



