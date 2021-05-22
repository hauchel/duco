# class to handle i2c 
# import i2ct as i2ct
# k=i2ct()
# k.menu()
import machine
from machine import I2C
import sys
import gc
import time

class i2ct():
    def __init__(self):
        self.pinSDA=machine.Pin(4)
        self.pinSCL=machine.Pin(5)
        self.con=I2C(scl=self.pinSCL, sda=self.pinSDA)
        self.target=0
        # debug only:
        self.inp=0
        self.inpAkt=False
        self.lasthash="2cbac32719086e89b856e17bd2a34f21032a51d2"
        self.newhash ="0a536a14db3b230247d4d90c3b33abff25b64382"
       
    def request(self, anz):
        try:
            rec=self.con.readfrom(self.target,anz)
            return rec
        except Exception as inst:
            print ("i2c req Exc: "+str(inst))
            return bytearray("X00")
    
    def send(self,txt):
        try:
            self.con.writeto(self.target,bytearray(txt) )
        except Exception as inst:
            print ("i2c send Exc: "+str(inst))
  
    def queryStatus(self):
        self.send("S")
        rec=self.request(3)
        try:
            return rec.decode("utf-8")
        except Exception as inst:
            print ("i2c queryStatus Exc: "+str(inst))
            return bytearray("X00")
    
    def check(self):
        # have to give slave time to prepare answer
        # do not use if another query is running 
        cnt=10
        while (cnt > 0):
            cnt-=1
            rec=self.queryStatus()
            if rec[0]=='B':
                print ('B')
                gc.collect() # or sleep
            else:
                return True
        return False
    
    def queryResult(self):
        self.send("R")
        rec=self.request(5) # must be 5 as decode fails on xff
        try:
            return int(rec.decode("utf-8"))
        except Exception as inst:
            print ("i2c queryResult Exc: "+str(inst))
            return 0
        
    def queryElapsed(self):
        self.send("E")
        rec=self.request(5) # must be 5 as decode fails on xff
        try:
            return int(rec.decode("utf-8"))
        except Exception as inst:
            print ("i2c queryEla Exc: "+str(inst))
            return 0
    
    def queryId(self):
        self.send("I")
        time.sleep_ms(10)    #it takes time
        rec=self.request(22)[:22] # must be 22
        print (rec)
        return rec.decode("utf-8")
               
    def sendHash(self,was):
        #print("Sending hash "+was)
        self.check()
        if was=='L':
            tx='L'+self.lasthash[0:20]
        elif was=='M':    
            tx='M'+self.lasthash[20:40]
        elif was=='N':    
            tx='N'+self.newhash[0:20]
        elif was=='O':    
            tx='O'+self.newhash[20:40]
        else:
            print ("Invalid")
            return
        self.send(tx)
    
    def send4Hash(self):
        start=time.ticks_ms()
        self.sendHash('L');
        self.sendHash('M');
        self.sendHash('N');
        self.sendHash('O');
        print ("Hashes sent ",time.ticks_diff(time.ticks_ms(),start))
        
    def info(self):
        print(" Free",gc.mem_free())
        print("          0123456789012345678901234567890123456789")
        print("Last ",len(self.lasthash),">"+self.lasthash+"<")
        print("New  ",len(self.newhash),">"+self.newhash+"<")
 
    def getch(self):
        while True:
            ch= sys.stdin.read(1)     
            if ch is not None:
                print (ch,end='')
                if (ch>='0') and (ch<='9'):
                    if (self.inpAkt):
                        self.inp=self.inp*10+ord(ch)-ord('0')
                    else:
                        self.inpAkt=True
                        self.inp=ord(ch)-ord('0')
                else:
                    self.inpAkt=False
                    return ch
                
    def menu(self):   
        while True:
            print("I>",end="")
            tmp=self.getch()
            try:
                if tmp=="d":
                     print("scan:",self.con.scan())
                elif tmp=="h":
                    self.send4Hash()                
                elif tmp=="i":
                    self.info()                
                elif tmp=="q":
                    print (self.queryStatus())
                elif tmp=="w":
                    print (self.queryResult())
                elif tmp=="e":
                    print (self.queryElapsed())
                elif tmp=="z":
                    print (self.queryId())
                elif tmp=="r":
                    print("Request ",self.target," ",self.inp)
                    print(self.request(self.inp))
                elif tmp=="t":
                    self.target=self.inp
                    print("Target ",self.target)
  
                elif tmp=="A":
                    print("Send A to ",self.target)
                    self.send("A")
                elif tmp=="H":
                    print("Send H ",self.target)
                    self.send("H")
                elif tmp=="L":
                    self.sendHash(tmp)
                elif tmp=="M":
                    self.sendHash(tmp)
                elif tmp=="N":
                    self.sendHash(tmp)
                elif tmp=="O":
                    self.sendHash(tmp)
                elif tmp=="S":
                    print("Send S to ",self.target)
                    self.send("S")
                elif tmp=="x":
                    return
                else:
                    print("d, q,w,e,z  h,r, q,w t  x  A H L M N O S ")
            except Exception as inst:
                print ("menu1 Exception "+str(inst))
        


