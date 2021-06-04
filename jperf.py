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


uname = "targon"
tick=10

import time
import sys
import json
import requests

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


def getBalance():    
    global connected  
    connected=False
    try:
        r=requests.get('https://server.duinocoin.com:5000/balances/'+jr.username)
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
        print('***getBalance for',jr.username,'success not true')
        return 0

def query(): 
    anf=0
    bal=0
    prev=0
    thistime=time.time()
    lasttime=thistime
    print(" Please wait, tick is",tick)  # 10 normal, else fast
    anf=float(getBalance())
    if not connected:
        print ('***No balance for',jr.username)
        return
    prev=anf
    ar=[0,0,0,0,0,0]
    su=0
    arP=0
    logN=time.strftime("_%d_%H.txt", time.localtime())
    if tick==10:  #just in case 2 sessions inquire same user
        logN='logs/perf_'+jr.username+logN
    else:
        logN='logs/fast_'+jr.username+logN
    logf = open(logN, "a")
    print("Logfile",logN)
    tx="Starting "+time.strftime("%c", time.localtime())+" with "+str(anf )
    logf.write(tx+"\n")
    print(tx)
    print("values below in milliDuco, allow 1 minute settling time")
    if tick==10:
        print( "Time          Total   Hash Mnr    10 sec    Minute    Duco/d") 
    else:
        print( "Time          Total   Hash Mnr  timedelt  increase") 
    while True:
        rest=tick - time.time() % tick   #time to sleep
        while rest>1:
            if kb.kbhit():
                logf.close()
                kb.forgetch()
                return
            time.sleep(1)
            rest-=1
        time.sleep(tick - time.time() % tick)    # wait exact
        thistime=time.time()
        txti=time.strftime("%H:%M:%S", time.localtime())
        # REST api
        bal=float(getBalance())
        show=2
        if tick != 10:
            if bal==prev:
                show=0
            else:
                show=1
        if show>0:
            txmi = "  {:2d}".format(jr.getMiners())    
            txha = " {:6d}".format(jr.getHashTotal()) 
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
            if show==1:   #fast
                txtd="  ({:6.3f})".format(thistime-lasttime)
                txs=txti+" "+tx99+txha+txmi+txtd+tx10
                txl=txti+" "+txab+txha+txmi+txtd+tx10
                lasttime=thistime
            else:
                txs=txti+" "+tx99+txha+txmi+tx10+txsu+txpd
                txl=txti+" "+txab+txha+txmi+tx10+txsu+txpd
            print (txs)
            logf.write(txl+"\n")
            
        prev=bal
        if not connected:   #something went wrong, close log
            logf.close()
            print ("query terminated")
            return
        if kb.kbhit():
            logf.close()
            kb.forgetch()
            return

def hilfe():
    print("              \n\
a  get AVR Top e.g 20a        \n\
b  Balance               \n\
q  Query         \n\
 \n\
o  show Other users     \n\
u  switchUser, e.g. 3u     \n\
s  Show topusers     \n\
t  switchTopuser (after getAVR!), e.g. 1t \n\
 \n\
f  Fast mode:   tick  1 second, only changes shown \n\
n  Normal mode: tick 10 seconds  \n\
 \n\
x  eXit          \n\
   \n")
        
def menu():   
    global tick
    global connected
    inpAkt=False
    inp=0
    query()
    connected =True
    # here after keypress 
    while True:
        if not inpAkt: print(jr.username,"P>",end='',flush=True)
        while  not connected:
            print ("Retry")
            query()
        try:
            ch = kb.getch()  
        except Exception as inst:
            print ("*** Don't use this key, Exception "+str(inst))
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
                elif ch=="b":
                    print(" Balance of ",jr.username,'is',getBalance())
                elif ch=="f":
                    tick=1
                    query()
                elif ch=="i":
                    jr.topUsers(inp,'I2C')                     
                elif ch=="n":
                    tick=10
                    query()                    
                elif ch=="q":
                    query()
                elif ch=="o":
                    jr.showUsers() 
                elif ch=="s":
                    jr.showTopsers()                       
                elif ch=="t":
                    if jr.switchTopser(inp):
                        query()                            
                elif ch=="u":
                    if jr.switchUser(inp): 
                        query()              
                elif ch=="x":
                    print(" Thanks for watching")
                    return
                elif ch=="#" or ch=='?':
                    hilfe()
                else:
                    print(" ? (ascii "+str(ord(ch))+"), type ? for help")
            except Exception as inst:
                print ("*** menu Exception "+str(inst))
                raise  #to ease fix
                
if len(sys.argv)>1:
    jr.username = sys.argv[1]
    print ("username is ",jr.username)                
menu()        

