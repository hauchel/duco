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

uname = "targon"
tick=10
sortby='software'  # any key to sort by
sortrev=False      # order
wide=False        # display of software and rig

import time
import sys
from operator import itemgetter

from kbhit import KBHit
kb = KBHit()

import jrests
jr=jrests.rests(uname)

try:
    import privusers as priv
    jr.users=priv.users
except ImportError:
    jr.users=[jr.username]    #0u is me  
    print("no privusers.py, having")
    print("user=['user0','user1','user2']")


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
    # 1:1
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
    logN='logs/min_'+jr.username+logN
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
                logf.close()
                kb.forgetch()
                return
            time.sleep(1)
            rest=tick - time.time() % tick
        time.sleep(tick - time.time() % tick)    # wait exact
        txti=time.strftime("%H:%M:%S", time.localtime())
        jr.getMiners()
        tx=txti+" Running " +' {:2}'.format(len(jr.uminers))+"                Diff      Acc/Rej      Hash      Time"
        print(tx)
        logf.write(tx+"\n")
        sumH=0
        sumArd=0
        if sortby=='':
            li=unsort(jr.uminers)
        else:
            li=sort(jr.uminers)
        for n in li:
            k=jr.uminers[n]
            txha='{:10.1f}'.format(k['hashrate'])
            sumH+=k['hashrate']
            if k['hashrate'] <250:      #Arduino only
                sumArd+=k['hashrate']
            if wide:
                txid=' {:25}'.format(k['identifier'][:25])
                txso='{:35}'.format(k['software'][:35])
            else:
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
            logf.close()
            kb.forgetch()
            return
        
def hilfe():
    print("              \n\
a  get AVR Top e.g 20a        \n\
j  Json with tick n   \n\
q  Query  tick 10        \n\
d  toggle display to show full names \n\
\n\
p  sort by accePted  \n\
h  sort by Hashrate  \n\
n  No sort \n\
w  sort by softWare  \n\
e  sort by Elapsed time  \n\
r  toggle Reverse \n\
\n\
o  show Other users     \n\
u  switch User, e.g. 3u     \n\
s  Show topusers     \n\
t  switch Topuser (after get AVR), e.g. 1t \n\
 \n\
x  eXit          \n\
 \n")
        
def afterSort(myTick):
    global sortby
    global sortrev    
    print(' Sort by',sortby)
    query(myTick)
    
def menu():   
    global sortby
    global sortrev
    global wide
    inpAkt=False
    myTick=10    #change by j
    inp=0
    query(10)
    # here after keypress 
    while True:
        if not inpAkt: print(jr.username,"M>",end='',flush=True)
        try:
            ch = kb.getch()  
        except Exception as inst:
            print ("don't use this key, Exception "+str(inst))
            ch='?'
        print(ch,end='',flush=True)
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
        else:
            inpAkt=False
            try:
                if ch==" ":
                    pass
                elif ch=="a":
                    jr.getAllMiners()
                    num=inp
                    if num<10: 
                        print ("assume minimum 10")
                        num=10
                        jr.topUsers(num,'AVR')  
                elif ch=="A":     #override 10
                    jr.topUsers(inp,'AVR')
                elif ch=="d":     
                    wide = not wide
                    print(" display wide",wide)
                    query(myTick)  
                elif ch=="e":
                    sortby='sharetime'
                    afterSort(myTick)                    
                elif ch=="h":
                    sortby='hashrate' 
                    afterSort(myTick)
                elif ch=="i":
                    jr.topUsers(inp,'I2C')                           
                elif ch=="j":
                    myTick=inp
                    if myTick<1: myTick=1
                    print(" Tick ",myTick)
                    query(myTick)
                elif ch=="n":
                    sortby=''
                    print(' No Sort')
                    query(myTick) 
                elif ch=="o":
                    jr.showUsers()                     
                elif ch=="p":
                    sortby='accepted'
                    afterSort(myTick)                    
                elif ch=="q":
                    query(10)
                elif ch=="r":
                    sortrev= not sortrev
                    print('Sort reverse',sortrev)
                    query(myTick)
                elif ch=="s":
                    jr.showTopsers()                       
                elif ch=="t":
                    if jr.switchTopser(inp):
                        query(myTick)                            
                elif ch=="u":
                    if jr.switchUser(inp):
                        query(myTick)    
                elif ch=="w":
                    sortby='software'
                    afterSort(myTick)                     
                elif ch=="x":
                    print(" Thanks for watching")
                    return
                elif ch=="#" or ch=='?':
                    hilfe()
                else:
                    print(" ? (ascii "+str(ord(ch))+"), type ? for help")
            except Exception as inst:
                print ("*** menu Exception "+str(inst))
                #raise  #to ease fix

                
if len(sys.argv)>1:
    jr.username = sys.argv[1]
    print ("username is ",jr.username) 
menu()        

