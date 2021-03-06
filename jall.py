# -*- coding: utf-8 -*-
# should run on win and raspi
#
# all balances or all miners, some experiments
# results written to /json
# 
# see https://github.com/dansinclair25/duco-rest-api

import time
import json
import requests
from operator import itemgetter
miners={}   #global, set by getMineers


from kbhit import KBHit
kb = KBHit()
connected=True
tick=10

def getBalances():    
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
    jsoN=time.strftime("json/bal_%d_%H%M%S.txt", time.localtime())
    print("to file",jsoN)
    with open(jsoN, 'w') as outfile:
        json.dump(jdic, outfile)
    outfile.close()  # required?
    return len(jdic)

def getAllMiners():    
    global connected  #TODO error checking
    global miners
    print('Please Wait...')
    try:
        r=requests.get('https://server.duinocoin.com:5000/miners')
    except Exception as inst:
        print ("getMiners Exception "+str(inst))
        connected=False
        return 0
    connected=True
    jdic=json.loads(r.text)
    miners=jdic['result']
    jsoN=time.strftime("json/min_%d_%H%M%S.txt", time.localtime())
    print("to file",jsoN)
    with open(jsoN, 'w') as outfile:
        json.dump(miners, outfile)
    outfile.close()
    return len(miners)

        

def readMinfile():
    global miners
    np='json/min_30_073631.txt'
    with open(np) as fil:
        miners = json.load(fil)
        print ("miners has",len(miners))
 

def readBalfiles(amnt):
    # compares two balfiles and shows chng > amnt
    global dp # dict with balance[user]
    global da 
    global dc
    np='json/bal_08_062507.txt'
    na='json/bal_12_054129.txt'
    with open(np) as fil:
        dpt = json.load(fil)
        print ("dp has",len(dpt))
        dp=dict()
        for p in dpt:
            dp[p['username']]=p['balance']
         
    with open(na) as fil:
        dat = json.load(fil)    
        print ("da has",len(dat))
        da=dict()
        for a in dat:
            da[a['username']]=a['balance']

    dc=dict()
    n=2500
    unc=0
    chg=0
    for key in dp:
        if (key in da):
            if da[key] != dp[key]:
                chg+=1
                diff=round((da[key]-dp[key]),2)
                if diff>amnt:
                    dc[key]=diff
                    print(key,"has",dc[key])
                if diff<0:
                    print(key,"lost",diff)                    
                n-=1
            else:
                unc+=1
        if n<1:
            break
    print ("unchanged",unc)
    print ("changed",chg)
    print ("major",len(dc))

def query():
    print("Using tick",tick,"One Moment...")
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
        getBalances()
        if kb.kbhit():
            print ("done")
            return

def hilfe():
    print("              \n\
b  Balances               \n\
f  Fast\n\
n  Normal \n\
m  miners, then only        \n\
   a  top AVR users e.g. 20a    \n\
t  top AVR Showusers     \n\
u  switchUser, e.g. 3u     \n\
x  eXit          \n\
   \n")
        
def menu():   
    inpAkt=False
    inp=0
    global tick
    #query()
    # here after keypress 
    while True:
        print("A>",end='',flush=True)
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
                    topAVR(inp)
                elif ch=="b":
                    print("Balances",getBalances())
                elif ch=="f":
                    tick=2
                    query()
                elif ch=="m":
                    pass
                elif ch=="n":
                    tick=10
                    query()
                elif ch=="q":
                    query()
                elif ch=="r":
                    
                    readBalfiles(inp)
                    print ("read")
                elif ch=="t":
                    readMinfile()
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

