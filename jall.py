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

def getMiners():    
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


def topAVR(min):
    global miners 
    global dn # sorted by count
    print ("Miners has",len(miners))
    dp=dict()
    n=8000
    for p in miners:
        n-=1
        if n<0:
            break
        if 'AVR' in p['software']:
            try:
                dp[p['username']]+=1
            except:
                dp[p['username']] =1
    dn= sorted(dp.items(),key=itemgetter(1),reverse=True)  # list of user,count
    print ("Count AVR Miners ge",min)
    str="users=['targon'"
    for m in dn:    # user,count
        if m[1]<min:
            break
        print(m[0],m[1])
        str+=",'"+m[0]+"'"
    str+="]"    
    print (str)
        

def readMinfile():
    global miners
    np='json/min_30_073631.txt'
    with open(np) as fil:
        miners = json.load(fil)
        print ("miners has",len(miners))
 

def readBalfiles():
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
                    print("Miners",getMiners())
                elif ch=="n":
                    tick=10
                    query()
                elif ch=="q":
                    query()
                elif ch=="r":
                    readMinfile()
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

