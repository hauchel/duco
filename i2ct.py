# class to handle i2c 
# import i2ct as i2ct
# k=i2ct()
# k.menu()
import machine
from machine import I2C
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
        self.difficulty=10


    def setSpeed(self,khz):
        self.con.init(self.pinSCL,self.pinSDA, freq=khz*1000)

    def request(self, anz):
        try:
            rec=self.con.readfrom(self.target,anz)
            return rec
        except Exception as inst:
            print (self.target,"i2c req Exc: "+str(inst))
            return bytearray("X00")
    
    def send(self,txt):
        try:
            self.con.writeto(self.target,bytearray(txt) )
        except Exception as inst:
            print (self.target,"i2c send Exc: "+str(inst))
  
    def queryStatus(self):
        self.send("S")
        rec=self.request(3)
        try:
            return rec.decode("utf-8")
        except Exception as inst:
            print (self.target,"i2c queryStatus Exc: "+str(inst))
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
        try:
            return rec.decode("utf-8")
        except: #not supported by slave
            return 'DUCOID8159497002237243'

    def setDifficulty(self):
        if self.difficulty>99: 
            self.difficulty=99
        tx="D{:02d}".format(self.difficulty)
        self.send(tx)

    def setTwiAdr(self,adr):
        tx="V{:02d}".format(adr)
        self.send(tx)


    def sendHash(self,was):
        #print("Sending hash "+was)
        self.check()
        if was=='L':
            tx=was+self.lasthash[0:20]
        elif was=='M':    
            tx=was+self.lasthash[20:40]
        elif was=='N':    
            tx=was+self.newhash[0:20]
        elif was=='O':    
            tx=was+self.newhash[20:40]
        else:
            print ("Invalid SendHash",was)
            return
        self.send(tx)
        
    def sendHash85(self,was):
        #print("Sending hash "+was)
        self.check()
        if was=='L':
            tx=was+self.lasthash[0:14]
        elif was=='M':    
            tx=was+self.lasthash[14:28]
        elif was=='N':    
            tx=was+self.lasthash[28:40]            
        elif was=='O':    
            tx=was+self.newhash[0:14]
        elif was=='P':    
            tx=was+self.newhash[14:28]
        elif was=='Q':    
            tx=was+self.newhash[28:40]
        else:
            print ("Invalid SendHash85",was)
            return
        self.send(tx)        
    
    def sendHashes(self):
        #start=time.ticks_ms()
        if self.target <50:
            for was in ['L','M','N','O']:
                self.sendHash(was);
        else: #tiny
            for was in ['L','M','N','O','P','Q']:
                self.sendHash85(was);
        #print ("Hashes sent ",time.ticks_diff(time.ticks_ms(),start))
        
