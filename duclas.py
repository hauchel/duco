# -*- coding: utf-8 -*-
# classes for duino

import socket
import time
import uselect

try:
    import requests
except ImportError:
    print("use urequests")
    import urequests as requests

try:   
    from i2ct import i2ct
    i2=i2ct()   # only one interface for all connections (!)
except ImportError:
    print("no i2ct")

class cserv():
    
    def __init__(self):    
        print ("Finding Server...")
        self.pool_address="51.15.127.80"
        self.pool_port =2811
        return
        soc = socket.socket()
        soc.settimeout(10)
        serverip = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")
        content = serverip.text.split("\n") # Read content and split into lines
        self.pool_address = content[0]  # Line 1 = pool address
        self.pool_port = int(content[1])  # Line 2 = pool port
        soc.connect((self.pool_address,self.pool_port))  # Connect to the server
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)
        soc.close()
    

class ccon():

    def __init__(self,targ,tarnam,pool_address,pool_port,rignam):    
        print ("Init ",targ)
        self.target=targ
        self.conTimOut=10
        self.tarnam=tarnam
        self.rignam=rignam
        self.pool_address=pool_address
        self.pool_port=pool_port
        self.lasthash=""
        self.newhash=""
        self.diffi=5
        self.sta='D'
        self.start=0
        self.poller=uselect.poll()
        self.sendRate=False    # False: let server calculate 
        self.verbose=False      # False: less prints
        self.ducoId="DUCOIDFFDFFFDFFFFFFFFF" #later queried from slave
        self.statReset()
        
    def statReset(self):
        self.reqAnz=0
        self.getJobWait=0
        self.getResWait=0
        self.tarBusy=0        
        self.tarEla=0
        self.tarSum=0
        
    def conn(self):    
        i2.target=self.target
        i2.send("A")  # reset slave
        self.getSlStat()
        self.ducoId=self.getDucoId()
        print ("Connecting...")
        self.soc = socket.socket()
        self.soc.settimeout(self.conTimOut) # low timeout as this blocks, will try again next loop
        self.start=time.ticks_ms()
        try:
            self.soc.connect((self.pool_address,self.pool_port))  
            self.soc.recv(3) #skip version
            self.sta='C'
            print ("Connect took ",time.ticks_diff(time.ticks_ms(),self.start))
        except Exception as inst:
            print ("Conn Exc TO",self.conTimOut,str(inst))
            self.sta='D'
        
    def reqJob(self,username = "targon"):
        tx="JOB," + username + ",AVR"
        if self.verbose: print("ReqJob",tx)
        try:
            self.soc.send(bytes(tx, "utf8"))  # Send job request
            self.sta='R'
            self.poller.register(self.soc,uselect.POLLIN)
            self.start=time.ticks_ms()
        except Exception as inst:
            print ("ReqJob Exc "+str(inst))
            self.sta='D'
            
    def getJob(self):
        if self.verbose: print("GetJob",self.sta)
        try:
            job = self.soc.recv(1024).decode()  # Get work from pool
            self.sta='J'
        except Exception as inst:
            print ("getJob Exc "+str(inst))
            self.sta='D'
            return
        tim=time.ticks_diff(time.ticks_ms(),self.start)
        print (self.target,"PER getJob took",tim)
        self.getJobWait+=tim
        self.reqAnz+=1
        job = job.split(",")  
        if len(job)>2:
            #print (job[0])
            self.lasthash=job[0]
            #print (job[1])
            self.newhash=job[1]
            #print (job[2])
            self.diffi=int(job[2])
        else:
            print ("Joblen?",len(job)," ",str(job),"<")
            self.sta='D'    
            
    def sndRes(self,res,rat):
        tx=  str(res) +  "," 
        if self.sendRate:
            tx=tx+ str(rat)  
        tx=  tx+ ","+self.tarnam+"," + self.rignam
        tx=  tx+ "," + self.ducoId
        if self.verbose: 
            print ("SndRes",self.sta,tx)
        try:
            self.soc.sendall(bytes(tx,'utf8'))
            self.sta='E'
            self.poller.register(self.soc,uselect.POLLIN)
            self.start=time.ticks_ms()
        except Exception as inst:
            print ("sndRes Exc "+str(inst))
            self.sta='D'
            return
    
    def getRes(self):
        if self.verbose: print("GetRes",self.sta)
        try:
            feedback = self.soc.recv(100).decode() 
            self.sta='C'
        except Exception as inst:
            print ("getdRes Exc "+str(inst))
            self.sta='D'
            return
        tim=time.ticks_diff(time.ticks_ms(),self.start)
        print (self.target,"PER getRes took",tim)
        self.getResWait+=tim
        print (self.target,feedback.rstrip())
              
    def close(self):
        self.sta='D'
        try:
            self.soc.close()
        except Exception as inst:
            print ("close Exc "+str(inst))
        print (self.target,"closed")

    def transfer(self):
        # to slave
        i2.lasthash=self.lasthash
        i2.newhash=self.newhash
        i2.target=self.target
        i2.send4Hash()  # to target
        self.sta='K'
    
    def getSlStat(self):
        # to slave
        i2.target=self.target
        t=i2.queryStatus()
        return t[:1]
   
    def getDucoId(self):
        # to slave
        i2.target=self.target
        t=i2.queryId()
        return t    
        
    def getResult(self):
        # to slave
        i2.target=self.target
        r=i2.queryResult()        
        return r
    
    def getElapsed(self):
        # to slave
        i2.target=self.target
        r=i2.queryElapsed()        
        return r
    
    def mach(self):
        # one step in loop
        # for those waiting for server don't inquire slave:
        i2.target=self.target
        t='W'
        if self.sta=='R': # fetch job
            if  not self.poller.poll(0):
                return t
            self.poller.unregister(self.soc)
            self.getJob()
            if self.sta == 'D':
                  print ("GetJob failed, status",self.sta)
                  return 'X'
            self.transfer()
            return t
        if self.sta=='E':  # fetch response
            if  not self.poller.poll(0):
                return t
            self.poller.unregister(self.soc)
  
            self.getRes()
            if self.sta=='D':
                  print ("GetRes failed")
                  return 'X'
            return t
                
        # slave related
        t=self.getSlStat()  # also switches i2.target
        if self.verbose: print ("*** ",self.target,"sla",t,"sta",self.sta)         
        if self.sta=='D':
            print ("Not Connected:")
            self.conn()
            return 'X'
        if t=="B":
            self.tarBusy+=1
            return t
        if self.sta=='C':
            self.reqJob()
            if self.sta == 'D':
                  print ("ReqJob failed, status",self.sta)
                  return 'X'
            return t
        if t=="C":
            res=self.getResult()
            ela=self.getElapsed()
            i2.send("A")  # reset slave 
            if ela!=0:
                rat=round(1000*res/ela)
                print(self.target,"ela:",ela,"res:",res,"rat:",rat)
                self.tarEla+=ela
                self.tarSum+=res
                self.sndRes(res,rat)
            else:
                print ("Ela Zero, why?")
            if self.sta=='D':
                  print ("SndRes failed")
                  return 'X'
            return t

        print("Sta Komisch?",self.sta)
        return 'X'
    
    def setVerbose(self,x):
        self.verbose=x
        print (self.tarnam," verbose ",str(self.verbose))
        
        
    def coninfo(self):
        print()
        print ("Target",self.target," sta",self.sta)
        print ("Name >"+self.tarnam+"< >"+self.ducoId+ "< sendrate"+str(self.sendRate))
        if self.reqAnz>0:
            print ("Requests ",self.reqAnz)
            tt=round(self.getJobWait/self.reqAnz)
            print ("ReqWait ",self.getJobWait, " per ",tt)
            tt=round(self.getResWait/self.reqAnz)
            print ("SndWait ",self.getResWait, " per ",tt)
            if self.tarEla >0:
                 tt=round(1000*self.tarSum/self.tarEla)
                 print ("Ela ", self.tarEla, "Res",self.tarSum, "Avg ",tt)
            tt=round(self.tarBusy/self.reqAnz)
            print ("Targ Busy ",self.tarBusy," per ",tt)         
        print ("Last",self.lasthash)
        print ("New ",self.newhash)
        print ("Diffi ",self.diffi)
