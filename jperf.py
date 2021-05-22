# -*- coding: utf-8 -*-
# should run on win and raspi
#
# Performance of duco: every 10 seconds query the balance of user 
# shows 10 seconds diff, one minute moving average
# logs written to /logs 
# 
# see https://github.com/dansinclair25/duco-rest-api
# {"result":{"balance":187.32699041006376,"username":"targon"},"success":true}\n


username = "targon"
try:
    import privusers as user
except ImportError:
    print("no privusers.py, having")
    print("user=['user0','user1','user2']")


import time
from datetime import datetime
import sys
import json
import requests

from kbhit import KBHit
kb = KBHit()
connected=True

def get_balance():
     global connected  #TODO error checking
     r=requests.get('https://server.duinocoin.com:5000/balances/'+username)
     jdic=json.loads(r.text)
     dic=jdic['result']
     return dic['balance']

def query():
    anf=0
    bal=0
    prev=0
    print("One Moment...")
    anf=float(get_balance())
    prev=anf
    ar=[0,0,0,0,0,0]
    su=0
    arP=0
    tick=10
    logN=time.strftime("_%d_%H.txt", time.localtime())
    logN='logs/perf_'+username+logN
    logf = open(logN, "a")
    print("Logfile",logN)
    tx="Starting "+time.strftime("%c", time.localtime())+" with "+str(anf )
    logf.write(tx+"\n")
    print(tx)
    print("values below in milliDuco                        ")
    print( "Time            Total  ping    10 sec    minute    Duco/d")  
    while True:
        rest=tick - time.time() % tick   #time to sleep
        while rest>1:
            if kb.kbhit():
                print ("Terminated")
                logf.close()
                return
            time.sleep(1)
            rest-=1
        time.sleep(tick - time.time() % tick)    # wait exact
        txti=time.strftime("%H:%M:%S", time.localtime())
        start=datetime.now()
        bal=float(get_balance())
        zwi=(datetime.now()-start).microseconds
        ping=round(zwi/1000)
        txpi = "{:6d}".format(ping) 
        dif10=bal-prev
        tx10="{:10.3f}".format(dif10*1000)  # this 10 secs
        dif99=bal-anf
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
        prev=bal
        if not connected:   #something went wrong
            logf.close()
            print ("query terminated")
            return
        if kb.kbhit():
            print ("done")
            logf.close()
            return


def switchuser(n):
    global username
    try:
        username=user.users[n]
        print ("username is ",username)
    except Exception as inst:
        print ("switchuser exception "+str(inst))
        print ("to use provide privusers.py with")
        print ("users=['user0','user1','user2']")
        
        

def hilfe():
    print("              \n\
a  Average #             \n\
b  Balance               \n\
q  query         \n\
x  eXit          \n\
                        \n")
        
def menu():   
    global username
    inpAkt=False
    inp=0
    myc=0  #current connect 
    query()
    # here after keypress 
    while True:
        print("P>",end=" ")
        ch = kb.getch()  
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
                    print("Balance ",get_balance())
                elif ch=="q":
                    query()
                elif ch=="u":
                    switchuser(inp)
                    query()
                   
                elif ch=="x":
                    return
                else:
                    print("else"+str(ord(ch)))
                    hilfe()
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #to ease fix
                
if len(sys.argv)>1:
    username = sys.argv[1]
print ("username is ",username)                
menu()        

