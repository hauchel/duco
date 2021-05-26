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
from operator import itemgetter

username='targon'
sortby='software'  # any key to sort by
sortrev=False      # order

try:
    import privusers as user
except ImportError:
    print("no privusers.py, having")
    print("user=['user0','user1','user2']")


from kbhit import KBHit
kb = KBHit()

def getMiners():
    try:
        r=requests.get('https://server.duinocoin.com:5000/miners?username='+username)
    except Exception as inst:
        print ("getMiners Exception "+str(inst))
        return {}
    jdic=json.loads(r.text)
    return jdic['result']    #  list of #miners dicts {}

def sort(ldic):
    # global sortby has key interested in
    # returns list of numbers pointing to entry in ldic
    ks=dict()
    n=0
    for d in ldic: # dictionary of sortby
        ks[n]= d[sortby]
        n+=1
    li=[]   #fill list with keys ordered by sortby
    for (key, value) in sorted(ks.items(),key=itemgetter(1), reverse=sortrev):
        li.append(key)
    return li

def unsort(ldic):
    # keys interested in
    li=[]
    n=0
    for l in ldic:
        li.append(n)
        n+=1
    return li
    
    
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
        dic=getMiners()
        tx=txti+" Running " +' {:2}'.format(len(dic))+"                Diff      Acc/Rej      Hash      Time"
        print(tx)
        logf.write(tx+"\n")
        sumH=0
        sumArd=0
        if sortby=='':
            li=unsort(dic)
        else:
            li=sort(dic)
        for n in li:
            k=dic[n]
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
        tx=txti+'      Tot{:10.1f}                   Arduino{:10.1f}'.format(sumH,sumArd)
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
j  Json with tick n   \n\
q  Query  tick 10        \n\
\n\
a  sort by accepted  \n\
h  sort by hashrate  \n\
n  no sort \n\
s  sort by software  \n\
t  sort by time  \n\
r toggle reverse \n\
\n\
f  show Friends   \n\
u  switch to User n then query fast      \n\
x  eXit          \n\
 \n")
        
def menu():   
    global username
    global sortby
    global sortrev
    inpAkt=False
    inp=0
    query(10)
    # here after keypress 
    while True:
        #print("M>",end=" ")# does not print
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
                    sortby='accepted'
                    print('Sort by',sortby)
                elif ch=="f":
                    showusers()      
                elif ch=="h":
                    sortby='hashrate'       
                    print('Sort by',sortby)
                elif ch=="j":
                    query(inp)
                elif ch=="n":
                    sortby=''
                    print('No Sort')
                elif ch=="q":
                    query(10)
                elif ch=="r":
                    sortrev= not sortrev
                    print('Sort reverse',sortrev)
                elif ch=="s":
                    sortby='software'
                    print('Sort by',sortby)
                elif ch=="t":
                    sortby='sharetime'
                    print('Sort by',sortby)
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

