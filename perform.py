# -*- coding: utf-8 -*-
# this is OUTDATED: better use jperf.py
# Performance of duco: every 10 seconds query the balance of user 
# shows 10 seconds diff, one minute moving average
# logs written to /logs 

username = "targon"
password = ""  # passed as parameter e.g. python perform.py secret

import socket
import time
from datetime import datetime
import sys



try:
    import requests
except ImportError:
    print("use urequests")
    import urequests as requests

try:
    import msvcrt
    def kbhit():
        return msvcrt.kbhit()    
    def getch():
        return msvcrt.getwch()
except ImportError:
    print("no msvcrt")
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
                if ord(tmp)>26:
                    return tmp

class cserv():
    
    def __init__(self):    
        print ("Finding Server...")
        self.pool_address="51.15.127.80"
        self.pool_port =2811
        soc = socket.socket()
        soc.settimeout(10)
        serverip = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")
        content = serverip.text.split("\n") 
        self.pool_address = content[0]  # Line 1 = pool address
        self.pool_port = int(content[1])  # Line 2 = pool port
        soc.connect((self.pool_address,self.pool_port)) 
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)
        soc.close()

serv=cserv()

class ccon():

    def __init__(self):    
        self.connected=False
        self.conn()
        self.bal=0
        self.prev=0
        self.anf=0
        

    def conn(self):    
        print ("Connecting...")
        self.soc = socket.socket()
        self.soc.settimeout(10)
        try:
            self.soc.connect((serv.pool_address,serv.pool_port))  
            self.soc.recv(3) #skip version
            self.connected =True
        except Exception as inst:
            print ("Conn Exception "+str(inst))
            self.connected=False
            
    def login(self, username, password):
        self.username = username
        self.password = password
        self.soc.send(f'LOGI,{username},{password}'.encode())
        login_result =self.soc.recv(64).decode()
        print ("Login",login_result)
        return login_result
            
    def get_balance(self):
        try:
            self.soc.send('BALA'.encode())
            balance = self.soc.recv(1024).decode()
            return float(balance)
        except Exception as inst:
            print ("get_balance Exception "+str(inst)+str(balance))
            self.connected=False
            return self.bal
    
    def close(self):
        self.soc.close()
        self.connected=False
        print ("closed")

    def query(self):
        print("One Moment...")
        self.anf=float(self.get_balance())
        self.prev=self.anf
        ar=[0,0,0,0,0,0]
        su=0
        arP=0
        logN=time.strftime("logs/perf%d_%H.txt", time.localtime())
        logf = open(logN, "a")
        print("Logfile",logN)
        tx="Starting "+time.strftime("%c", time.localtime())+" with "+str(self.anf )
        logf.write(tx+"\n")
        print(tx)
        print("values below in milliDuco                        ")
        print( "Time            Total  ping    10 sec    minute    Duco/d")  
        while True:
            time.sleep(10 - time.time() % 10)
            txti=time.strftime("%H:%M:%S", time.localtime())
            start=datetime.now()
            self.bal=float(self.get_balance())
            zwi=(datetime.now()-start).microseconds
            ping=round(zwi/1000)
            txpi = "{:6d}".format(ping) 
            dif10=self.bal-self.prev
            tx10="{:10.3f}".format(dif10*1000)  # this 10 secs
            dif99=self.bal-self.anf
            tx99="{:12.3f}".format(dif99*1000)  # from start
            su=su-ar[arP]+dif10                 # moving average / min
            ar[arP]=dif10
            arP+=1
            if(arP>5):
                arP=0
            txsu="{:10.3f}".format(su*1000)
            txpd="{:10.2f}".format(su*1440) #per day
            tx=txti+" "+tx99+txpi+tx10+txsu+txpd
            print (tx)
            logf.write(tx+"\n")
            self.prev=self.bal
            if not self.connected:   #something went wrong
                logf.close()
                print ("query terminated")
                return
            if kbhit():
                print ("done")
                logf.close()
                return
            

def hilfe():
    print("              \n\
a  Average #             \n\
b  Balance               \n\
c  Conn                  \n\
d  Down (close)          \n\
l  Login         \n\
n  New           \n\
q  query         \n\
x  eXit          \n\
                        \n")
        
def menu():   
    global myCon
    inpAkt=False
    inp=0
    myc=0  #current connect 
    myCon=ccon()
    myCon.login(username,password)
    myCon.query()
    # here after keypress 
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
                    print ("myc=",myc)
                elif ch=="b":
                    myCon.get_balance()                 
                elif ch=="c":
                    myCon.conn()
                elif ch=="d":
                    myCon.close()
                elif ch=="l":
                    myCon.login(username,password)
                elif ch=="n":
                    myCon=ccon()
                elif ch=="q":
                    myCon.query()
                elif ch=="x":
                    myCon.close()
                    return
                else:
                    print("else"+str(ord(ch)))
                    hilfe()
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #to ease fix
password = sys.argv[1]
print ("password used",password)
menu()        

