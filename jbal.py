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


import time
import json
import requests

from kbhit import KBHit
kb = KBHit()
connected=True

def get_balances():    
    global connected  #TODO error checking
    try:
        r=requests.get('https://server.duinocoin.com:5000/balances')
    except Exception as inst:
        print ("get_balances Exception "+str(inst))
        connected=False
        return 0
    connected=True
    jdic=json.loads(r.text)
    jdic=jdic['result']
    jsoN=time.strftime("json/bal__%d_%H%M%S.txt", time.localtime())
    print("to file",jsoN)
    with open(jsoN, 'w') as outfile:
        json.dump(jdic, outfile)
    outfile.close()

def readfiles():
    global dp # dict with balance[user]
    global da 
    global dc
    np='json/bal__25_212530.txt'
    na='json/bal__25_212540.txt'
    with open(np) as fil:
        dpt = json.load(fil)
        dpt=dpt['result']
        print ("dp has",len(dpt))
        dp=dict()
        for p in dpt:
            dp[p['username']]=p['balance']
         
    with open(na) as fil:
        dat = json.load(fil)    
        dat=dat['result']
        print ("da has",len(dat))
        da=dict()
        for a in dat:
            da[a['username']]=a['balance']

    dc=dict()
    n=1500
    u=0
    for key in dp:
        if (key in da):
            if da[key] != dp[key]:
                dc[key]=round(1000*(da[key]-dp[key]),3)
                print(key,"has",dc[key])
                n-=1
            else:
                u+=1
        if n<1:
            break
    print ("unchanged",u)
    print ("changed",len(dc))

def query():
    print("One Moment...")
    tick=10
    print( "Time            Total  ping    10 sec    minute    Duco/d")  
    while True:
        rest=tick - time.time() % tick   #time to sleep
        while rest>1:
            if kb.kbhit():
                print ("Terminated")
                return
            time.sleep(1)
            rest-=1
        time.sleep(tick - time.time() % tick)    # wait exact
        txti=time.strftime("%H:%M:%S", time.localtime())
        print (txti)
        get_balances()
        if kb.kbhit():
            print ("done")
            return

def hilfe():
    print("              \n\
a  Average  #TODO        \n\
b  Balance               \n\
q  query         \n\
s  Showusers     \n\
u  switchUser, e.g. 3u     \n\
x  eXit          \n\
   \n")
        
def menu():   
    inpAkt=False
    inp=0
    #query()
    # here after keypress 
    while True:
        print("P>",end=" ")
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
                    pass
                elif ch=="b":
                    print("Balances",get_balances())
                elif ch=="q":
                    query()
                elif ch=="r":
                    readfiles()
                    print ("read")
                elif ch=="u":
                    pass
                    query()              
                elif ch=="x":
                    return
                else:
                    print("else "+str(ord(ch)))
                    hilfe()
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #to ease fix
                
menu()        

