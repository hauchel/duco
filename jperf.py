# -*- coding: utf-8 -*-
# should run on win and raspi
#
# Performance of duco: every 10 seconds query the balance of user 
# shows 10 seconds diff, one minute moving average
# logs written to /logs   perf_username_day_hour.txt
# logs contain the total balance while screen shows
# growth since start of program
# 
# see https://github.com/dansinclair25/duco-rest-api
# {"result":{"balance":187.32699041006376,"username":"targon"},"success":true}\n


username = "targon"
miners={} # filled by getMiners 
tick=10

try:
    import privusers as user
except ImportError:
    print("no privusers.py, having")
    print("user=['user0','user1','user2']")

import time
import sys
import json
import requests

from kbhit import KBHit
kb = KBHit()
connected=True

def getMiners():
    global miners
    miners={}
    try:
        r=requests.get('https://server.duinocoin.com:5000/miners?username='+username)
        jdic=json.loads(r.text)
        if jdic['success']==True:
                miners=jdic['result']
                return len(miners)
        else:
            print('***getMiners for',username,'success not true')
            return 99
    except Exception as inst:
        print ("***getMiners Exception "+str(inst))
        return 99

def getHashTotal():
    global miners # must be filled by getMiners first
    hash=0;
    for m in miners:
        hash+=m['hashrate']
    return round(hash)


def getBalance():    
    global connected  
    connected=False
    try:
        r=requests.get('https://server.duinocoin.com:5000/balances/'+username)
    except Exception as inst:
        print ("***getBalance Exception "+str(inst))
        return 0
    jdic=json.loads(r.text)
    if jdic['success']==True:
           dic=jdic['result']
           connected=True
           return dic['balance']
    else:
        print(jdic['success'])
        print (r.text)
        print('***getBalance for',username,'success not true')
        return 0

 
def query(): 
    anf=0
    bal=0
    prev=0
    print("One Moment...")
    anf=float(getBalance())
    if not connected:
        print ('***No balance for',username)
        return
    prev=anf
    ar=[0,0,0,0,0,0]
    su=0
    arP=0
    logN=time.strftime("_%d_%H.txt", time.localtime())
    logN='logs/perf_'+username+logN
    logf = open(logN, "a")
    print("Logfile",logN)
    tx="Starting "+time.strftime("%c", time.localtime())+" with "+str(anf )
    logf.write(tx+"\n")
    print(tx)
    print("values below in milliDuco, allow 1 minute settling time")
    print( "Time          Total   Hash Mnr    10 sec    Minute    Duco/d")  
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
        # REST api
        bal=float(getBalance())
        txmi = "  {:2d}".format(getMiners())    
        txha = " {:6d}".format(getHashTotal()) 
        # prepare
        dif10=bal-prev
        tx10="{:10.3f}".format(dif10*1000)  # this 10 secs
        dif99=bal-anf
        tx99="{:10.3f}".format(dif99*1000)  # from start
        su=su-ar[arP]+dif10                 # moving average / min
        ar[arP]=dif10
        arP+=1
        if(arP>5):
            arP=0
        txsu="{:10.3f}".format(su*1000)     # per minute   
        txpd="{:10.2f}".format(su*1440)     # per day
        txab="{:15.6f}".format(bal)         # abs for logf
        # write
        tx=txti+" "+tx99+txha+txmi+tx10+txsu+txpd
        print (tx)
        tx=txti+" "+txab+txha+txmi+tx10+txsu+txpd
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
        
def showusers():
    try:
        print("friends and foes:")
        n=0
        for u in user.users:
            print ("{:2d} ".format(n),u)
            n+=1
    except Exception as inst:
        print ("showusers exception "+str(inst))
        print ("to use provide privusers.py with")
        print ("users=['user0','user1','user2']")

def hilfe():
    print("              \n\
a  Average  #TODO        \n\
b  Balance               \n\
q  query         \n\
 \n\
s  Showusers     \n\
u  switchUser, e.g. 3u     \n\
 \n\
f  Fast mode:    tick 2 seconds \n\
n  Normal mode: tick 10 seconds  \n\
 \n\
x  eXit          \n\
   \n")
        
def menu():   
    global username
    global tick
    inpAkt=False
    inp=0
    query()
    # here after keypress 
    while True:
        if not inpAkt: print(username,"P>",end='',flush=True)
        try:
            ch = kb.getch()  
        except Exception as inst:
            print ("Don't use this key, Exception "+str(inst))
            ch='?'
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
            print(ch,end='',flush=True)
        else:
            print(ch)
            inpAkt=False
            try:
                if ch=="a":
                    pass
                elif ch=="b":
                    print("Balance ",getBalance())
                elif ch=="f":
                    tick=2
                    query()
                elif ch=="n":
                    tick=10
                    query()                    
                elif ch=="q":
                    query()
                elif ch=="s":
                    showusers()                
                elif ch=="u":
                    switchuser(inp)
                    query()              
                elif ch=="x":
                    return
                else:
                    print("else "+str(ord(ch)))
                    hilfe()
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #to ease fix
                
if len(sys.argv)>1:
    username = sys.argv[1]
print ("username is ",username)                
menu()        

