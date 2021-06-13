# -*- coding: utf-8 -*-
# classes for duino, currently at the limit for getting compiled on ESP 12...
# 

import socket
import time
import uselect
#import urequests as requests

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
#        soc = socket.socket()
#        soc.settimeout(10)
#        serverip = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")
#        content = serverip.text.split("\n") # Read content and split into lines
#        self.pool_address = content[0]  # Line 1 = pool address
#        self.pool_port = int(content[1])  # Line 2 = pool port
#        soc.connect((self.pool_address,self.pool_port))  # Connect to the server
#        server_version = soc.recv(3).decode()  # Get server version
#        print("Server is on version", server_version)
#        soc.close()
    

class ccon():

    def __init__(self,targ,tarnam,pool_address,pool_port,rignam):    
        print ("Init ",targ)
        self.target=targ
        self.tarnam=tarnam
        self.rignam=rignam
        self.pool_address=pool_address
        self.pool_port=pool_port
        self.lasthash=""
        self.newhash=""
        self.result=0
        self.ela=0
        self.difficulty=10
        self.sta='D'
        self.start=0
        
        self.poller=uselect.poll()
        self.sendRate=False     # False: let server calculate 
        self.verbose=False      # False: less prints
        self.ducoId=""          # queried from slave
        self.statReset()
        
    def statReset(self):        # for statistics
        self.reqAnz=0           # number of reqs processed
        self.reqAnzTop=0        # max for tests, 0=no limit
        self.getJobWait=0       # sum of waiting for job
        self.getResWait=0       # sum of waiting for result
        self.jobStartTim=0      # time of job Start
        self.jobRecvTim=0       # time of receiving job
        self.jobContTim=0       # time to continue job in state W
        self.tarBusy=0          #
        self.tarRetry=0         # sum of retries
        self.tarFault=0         # current retries in state W
        self.tarEla=0           # elapsed
        self.tarSum=0
        
    def conn(self):    
        i2.target=self.target
        i2.send("A")  # reset slave
        self.getSlStat()
        self.ducoId=self.getDucoId()
        print (self.target,"Connecting...")
        self.soc = socket.socket()
        self.soc.settimeout(10) # low timeout as this blocks, will try again next loop
        self.start=time.ticks_ms()
        try:
            self.soc.connect((self.pool_address,self.pool_port))  
            print ("Connected") 
            self.sta='V'
            self.poller.register(self.soc,uselect.POLLIN)
        except Exception as inst:
            print ("Conn Exc",inst)
            self.sta='D'
        
    def conn2(self):  
        try:              
            self.soc.recv(3) #skip version
            self.sta='C'
            print ("Connect took ",time.ticks_diff(time.ticks_ms(),self.start))
        except Exception as inst:
            print ("Conn2 Exc",inst)
            self.sta='D'
        
    def reqJob(self,username = "targon"):
        tx="JOB," + username + ",AVR"
        if self.verbose: print(self.target,"ReqJob",tx)
        try:
            self.soc.send(bytes(tx, "utf8"))  # Send job request
            self.sta='R'
            self.poller.register(self.soc,uselect.POLLIN)
            self.start=time.ticks_ms()
            self.jobStartTim=self.start
        except Exception as inst:
            print (self.target,"ReqJob Exc "+str(inst))
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
        self.jobRecvTim=time.ticks_ms()
        self.jobContTim=0
        tim=time.ticks_diff(self.jobRecvTim,self.start)
        print (self.target,"PER getJob took",tim)
        self.getJobWait+=tim
        job = job.split(",")  
        if len(job)>2:
            #print (job[0])
            self.lasthash=job[0]
            #print (job[1])
            self.newhash=job[1]
            #print (job[2])
            self.difficulty=int(job[2])
            if self.verbose: print(self.target,job[0],job[1],job[2])
        else:
            print (self.target,"Joblen?",len(job)," ",str(job),"<")
            self.sta='D'    
            
    def sndRes(self):
        tx=  str(self.result) +  "," 
        if self.sendRate:
            rat=round(1000*self.result/self.ela)
            tx=tx+ str(rat)  
        tx=  tx+ ","+self.tarnam+"," + self.rignam
        tx=  tx+ "," + self.ducoId
        #if self.result==0:
        #    print(self.target,tx)
        #    self.sta='C'                
        #    return
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
            print (self.target,"getRes Exc "+str(inst))
            self.sta='D'
            return
        now=time.ticks_ms()
        tim=time.ticks_diff(now,self.start)
        timtot=time.ticks_diff(now,self.jobStartTim)
        self.reqAnz+=1
        self.getResWait+=tim
        print (self.target,"PER getRes took",tim)
        print (self.target,feedback.rstrip(),"took",timtot) 
              
    def close(self):
        self.sta='D'
        try:
            self.soc.close()
        except Exception as inst:
            print ("close Exc "+str(inst))
        print (self.target,"closed")

    def transfer(self):
        # to slave
        i2.send("A")  # state 'C' would not change, so reset
        i2.lasthash=self.lasthash
        i2.newhash=self.newhash
        i2.target=self.target
        i2.difficulty=self.difficulty
        i2.sendHashes() 
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
        # bad performance if using same ducoid?
        t=t[:6]+str(self.target-5)+str(self.target+5)+t[10:]
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
        now=time.ticks_ms()
        t='Y' 
        
        if self.sta=='V': # waiting for connection
            if  self.poller.poll(0):
                self.conn2()
                self.poller.unregister(self.soc)
            else:
                if time.ticks_diff(now,self.start)>15000: # more than 15 secs retry
                      self.poller.unregister(self.soc)
                      self.sta='D'                
            return t
        
        if self.sta=='R': # waiting for fetch job
            if  not self.poller.poll(0): #have to avoid beeing caught here
                tim=time.ticks_diff(now,self.jobStartTim)
                if tim>20000:
                    print (self.target,"R Time? ",tim)
                    self.poller.unregister(self.soc)
                    self.sta='D'
                return t
            self.poller.unregister(self.soc)
            self.getJob()
            if self.sta == 'D':
                  print (self.target,"GetJob failed, status",self.sta)
                  return 'X'
            self.transfer()
            return t
        
        if self.sta=='W':   # speed limiter
            #if self.result==0:
            #    print (self.target, "Retry",self.tarFault)
            #    self.tarRetry+=1
            #    self.tarFault+=1
            #    if self.tarFault<3:
            #        self.transfer()  # changes state to 'K'
            #    else:
            #        self.sta='C'     # give up
            #    return t
            #self.tarFault=0   
                
            self.sndRes()   # changes state to 'E'
            return t        # not needed
            #if self.jobContTime==0: #TODO
            #    self.jobContTime=now+2000
            #else:
            #    if now>self.jobContTime: 
            #        self.sndRes()  # changes state to 'E'
            #return t
        
        if self.sta=='E':  # fetch response
            if  not self.poller.poll(0):
                tim=time.ticks_diff(now,self.jobStartTim)
                if tim>30000:   # if job took so long, something is kaputt
                    print (self.target,"E Time? ",tim)
                    self.poller.unregister(self.soc)
                    self.sta='D'
                return t
            self.poller.unregister(self.soc)
  
            self.getRes()
            if self.sta=='D':
                  print (self.target,"GetRes failed")
                  return 'X'
            return t
         
        # check top
        if self.reqAnzTop>0:
            if self.reqAnz>=self.reqAnzTop:
                return 'Z'
            
        # slave related
        t=self.getSlStat()  # also switches i2.target
        #if self.verbose: print ("*** ",self.target,"sla",t,"sta",self.sta)         
        if self.sta=='D':
            print (self.target,"Not Connected")
            self.conn()
            return 'X'
        if t=="B":
            self.tarBusy+=1
            return t
        if self.sta=='C':
            self.reqJob()
            if self.sta == 'D':
                  print (self.target,"ReqJob failed")
                  return 'X'
            return t
        if t=="C":
            self.result=self.getResult()
            self.ela=self.getElapsed()
            i2.send("A")  # reset slave 
            self.sta='W'
            if self.ela!=0:
                rat=round(1000*self.result/self.ela)
                print(self.target,"ela:",self.ela,"res:",self.result,"rat:",rat)
                self.tarEla+=self.ela
                self.tarSum+=self.result

            if self.sta=='D':
                  print (self.target,"SndRes failed")
                  return 'X'
            return t
        # typical slave status exception.
        print(self.target,"ERR Sta Komisch?",self.sta)
        time.sleep(0.1)
        self.tarRetry+=1
        return 'X'
    
    def setVerbose(self,x):
        self.verbose=x
        print (self.tarnam," verbose ",str(self.verbose))
        
    def coninfo(self):
        print()
        print ("Target",self.target," sta",self.sta,"retry",self.tarRetry)
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
#        print ("Last",self.lasthash)
#        print ("New ",self.newhash)
#        print ("Diffi ",self.difficulty)
