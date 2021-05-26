# -*- coding: utf-8 -*-

import sys
import gc
import time

try:
    import msvcrt
    def kbhit():
        return msvcrt.kbhit()    
    def getch():
        return msvcrt.getwch()
except ImportError:
    print("Assuming on ESP")
    import uselect
    def kbhit():
        spoll=uselect.poll()
        spoll.register(sys.stdin,uselect.POLLIN)
        kbch = sys.stdin.read(1) if spoll.poll(0) else None
        spoll.unregister(sys.stdin)
        return(kbch)
    
    def getch():
        while True:
            tmp= sys.stdin.read(1)     
            if tmp is not None:
                return tmp
try:   
    from i2ct import i2ct
    i2=i2ct()
    print ("Available Slaves:", i2.con.scan())
    
except ImportError:
    print("no i2ct")

from duclas import cserv
from duclas import ccon

username="targon"    
rigname = "None"
myCons=[]

serv=cserv()

def newCon(targ,tarnam):
     myCons.append(ccon(targ,tarnam,serv.pool_address, serv.pool_port,rigname))
    
def get_config():
    global rigname
    conf=open("conf.txt",'r')
    rigname=conf.readline().rstrip()
    print (rigname)
    for l in conf.readlines():
        s=l.rstrip().split(" ",1)
        print (s[1]+"<")
        newCon(int(s[0]),s[1])
        
def overview():
    print("cons",len(myCons))
    now=time.ticks_ms()
    for c in myCons:
        tim=time.ticks_diff(now,c.jobStart)    
        print (c.target, c.getSlStat(),c.sta,"sin", tim)

def info():
    gc.collect()
    print ("Available Slaves:", i2.con.scan())
    print("Free",gc.mem_free())
    #print("pool_address",serv.pool_address)
    #print("pool_port",serv.pool_port)
    print("rigname",rigname)
    print(len(myCons)," Cons:")
    for c in myCons:
        c.coninfo()

def loop():
    global myCons
    allbusy=0       #counter subsequent loops
    ms='?'
    now=time.ticks_ms()
    for c in myCons:   #
        c.jobStart=now
    while True:
        allbusy=allbusy+1
        for c in myCons:
            ms=c.mach()
            if ms != 'B':
                allbusy=0
        if kbhit() is not None:
            break
        if allbusy>0:
            print("All Bus ",allbusy)
            gc.collect()    # something useful
            time.sleep(0.1)
    print("Loop Done")

 
def menu():   
    global myCons
    inpAkt=False
    inp=0
    myc=0
    verbose = True
    print (username+", welcome to mydu. Use s to start:") 
    print ("... then l to loop:")
    if  len(myCons)==0:  #re-running config would duplicate cons
        get_config()
        loop()
    while True:
        print("H>",end=" ")
        ch = getch()  
        print(ch)
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
        else:
            inpAkt=False
            try:
                if ch=="a":
                    myc=inp
                    print("myc=",myc)
                elif ch=="c":
                    myCons[inp].conn()
                elif ch=="d":
                    myCons[inp].close()
                    myCons.pop(inp)
                elif ch=="h":
                    myCons[inp].sendRate = not myCons[inp].sendRate
                    print ("sendRate ",myCons[inp].sendRate)
                elif ch=="i":
                    info()               
                elif ch=="l":
                    loop()  
                elif ch=="m":
                    myCons[inp].mach()                     
                elif ch=="o":
                    overview()  
                elif ch=="q":
                    print (myCons[inp].getSlStat())
                elif ch=="s":
                    get_config()
                elif ch=="t":
                    myCons[myc].conTimOut=inp
                    print (myc," Connection Timeout ",inp)
                elif ch=="u":
                    myCons[inp].statReset() 
                    print ("stats reset for",inp)
                elif ch=="v":
                    verbose = not verbose
                    for c in myCons:
                         c.setVerbose(verbose)
                elif ch=="w":
                    inp=myCons[myc].getResult()
                    print ("inp",inp)
                elif ch=="x":
                    for c in myCons:
                        c.close()
                    print ("Thanks for using mydu")
                    return
                else:
                    print("else"+str(ord(ch)))
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #remove when perfect

menu()        

