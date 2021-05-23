# -*- coding: utf-8 -*-
# should run on win and raspi
#
# every 10 seconds query the miners of user
# see https://github.com/dansinclair25/duco-rest-api
# "accepted":270,
# "algorithm":"DUCO-S1",
# "diff":5,
# "hashrate":195.0,
# "identifier":"Rig 41",
# "rejected":0,
# "sharetime":1.449807,
# "software":"I2C 15 AVR newMiner (DUCO-S1A) v2.47",
# "threadid":"139693169389640","
# "username":"targon"},
#
# logs written to /logs 

import time
#from datetime import datetime
import sys
import json
import requests

username='targon'
try:
    import privusers as user
except ImportError:
    print("no privusers.py, having")
    print("user=['user0','user1','user2']")


from kbhit import KBHit
kb = KBHit()

def query(tick):    
    print("Press any key to abort  <<<<")
    print("keyboard only checked every second")
    logN=time.strftime("_%d_%H.txt", time.localtime())
    logN='logs/min_'+username+logN
    print("Logfile",logN)
    logf = open(logN, "a")
 
    tx="Starting "+time.strftime("%c", time.localtime())
    logf.write(tx+"\n")
    print(tx)
    print("Tick ",tick) 
    while True:
        rest=tick - time.time() % tick   #time to sleep
        while rest>1:
            if kb.kbhit():
                print ("Terminated")
                logf.close()
                return
            time.sleep(1)
            rest=tick - time.time() % tick
        time.sleep(tick - time.time() % tick)    # wait exact
        txti=time.strftime("%H:%M:%S", time.localtime())
        r=requests.get('https://server.duinocoin.com:5000/miners?username='+username)
        jdic=json.loads(r.text)
        dic=jdic['result']
        tx=txti+" Running " +' {:2}'.format(len(dic))+"                Diff      Acc/Rej      Hash      Time"
        print(tx)
        logf.write(tx+"\n")
        sumH=0
        sumArd=0
        for k in dic:
            txha='{:10.1f}'.format(k['hashrate'])
            sumH+=k['hashrate']
            if k['hashrate'] <250:      #Arduino only
                sumArd+=k['hashrate']
            txid=' {:7}'.format(k['identifier'][:7])
            txso='{:25}'.format(k['software'][:25])
            txsh='{:10.3f}'.format(k['sharetime'])
            txac= ' {:6d} '.format(k['accepted'])
            txdi= ' {:6d} '.format(k['diff'])
            txre= ' R{:2d}'.format(k['rejected'])
            tx=txid+txso+txdi+txac+txre+txha+txsh
            print (tx)
            logf.write(tx+"\n")
        tx=txti+'      Tot{:10.1f}                       Ard{:10.1f}'.format(sumH,sumArd)
        print (tx)
        logf.write(tx+"\n")

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
j  Json with tick n   \n\
q  Query  tick 10        \n\
u  switch to User n then query fast      \n\
x  eXit          \n\
 \n")
        
def menu():   
    global username
    inpAkt=False
    inp=0
    myc=0  #current connect
    query(10)
    # here after keypress 
    while True:
        #print("M>",end=" ")
        print("M>")
        ch = kb.getch()  
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
            print(inp)
        else:
            print(ch)
            inpAkt=False
            try:
                if ch=="a":
                    myc=inp
                    print ("myc=",myc)
                elif ch=="j":
                    query(inp)
                elif ch=="n":
                    pass
                elif ch=="q":
                    query(10)
                elif ch=="u":
                    switchuser(inp)
                    query(2)

                elif ch=="x":
                    print("thanks for watching")
                    return
                else:
                    print("else"+str(ord(ch)))
                    hilfe()
            except Exception as inst:
                print ("menu Exception "+str(inst))
                #raise  #to ease fix

if len(sys.argv)>1:
    username = sys.argv[1]
print ("username is ",username)
menu()        

