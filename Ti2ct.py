# to test i2ct 
from machine import I2C
import gc
import time
import sys

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
            ch= sys.stdin.read(1)     
            if ch is not None:
                return ch
try:   
    from i2ct import i2ct
    i2=i2ct()
    print ("Available Slaves:", i2.con.scan())
    
except ImportError:
    print("no i2ct")
    
        
def info():
    gc.collect()
    print(" Free",gc.mem_free())
    print("          01234567890123x56789o1234567x90123456789")
    print("Last ",len(i2.lasthash),">"+i2.lasthash+"<")
    print("New  ",len(i2.newhash),">"+i2.newhash+"<")
 
            
def menu():   
    inpAkt=False
    inp=0
    while True:
        if not inpAkt: print(i2.target,">",end='')
        ch = getch()  
        print(ch,end='')
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
        else:
            inpAkt=False
            try:
                if ch=="d":  #only from 0x08 to 0x77
                     print("scan:",i2.con.scan())
                elif ch=="e":
                    print (i2.queryElapsed())
                elif ch=="f":
                    i2.difficulty=inp
                    i2.setDifficulty()  
                elif ch=="h":
                    i2.sendHashes()                
                elif ch=="i":
                    info()                
                elif ch=="q":
                    print (i2.queryStatus())
                elif ch=="r":  #debug only, response could change if slave still working
                    print("Request ",i2.target," ",inp)
                    print(i2.request(inp))
                elif ch=="s":
                    print ("speed",inp)  
                    i2.setSpeed(inp) 
                elif ch=="t":
                    i2.target=inp
                    print("Target ",i2.target)
                elif ch=="v":
                    print (" addr",inp)  
                    i2.setTwiAdr(inp)                     
                elif ch=="w":
                    print (i2.queryResult())              
                elif ch=="z":
                    print (i2.queryId())
      
                elif ch=="A":
                    print(ch, "to",i2.target)
                    i2.send(ch)
                elif ch=="C":
                    print(ch, "to",i2.target)
                    i2.send(ch)
                elif ch=="H":
                    print(ch, "to",i2.target)
                    i2.send(ch)
                elif (ch>="L") and (ch<="Q"):
                    if self.target >49:
                        i2.sendHash85(ch)
                    else:
                        i2.sendHash(ch)
                elif ch=="S":
                    print("Send S to ",i2.target)
                    i2.send("S")
                elif ch=="x":
                    return
                else:
                    print("?")
            except Exception as inst:
                print ("menu1 Exception "+str(inst))
    

menu()        
