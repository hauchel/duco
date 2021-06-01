# -*- coding: utf-8 -*-
#common routines for jmin and jperf
import json
import requests
from operator import itemgetter

class rests:
    
    def __init__(self,unam):    
        print ("Welcome",unam)
        self.connected=True
        self.miners={}      # filled by getAllMiners 
        self.uminers={}     # filled by getMiners for user 
        self.topsers=[]     # filled by topusers
        self.users=[]       # from privusers
        self.username=unam
    
    def getAllMiners(self):    
        print(' Please Wait...')
        try:
            r=requests.get('https://server.duinocoin.com:5000/miners')
        except Exception as inst:
            print ("*** getMiners Exception "+str(inst))
            self.connected=False
            return 0
        self.connected=True
        jdic=json.loads(r.text)
        self.miners=jdic['result']
        return len(self.miners)   
    
    def topUsers(self,min,txt):
        # returns users with at least min miners having txt in software
        print (len(self.miners),"Miners active")
        dp=dict()
        n=8000
        for p in self.miners:
            n-=1
            if n<0:
                break
            if txt in p['software']:
                try:
                    dp[p['username']]+=1
                except:
                    dp[p['username']] =1
        dn= sorted(dp.items(),key=itemgetter(1),reverse=True)  # list of user,count
        print ('users with at least',min,txt,'Miners:')
        self.topsers=[]
        for m in dn:    # user,count
            if m[1]<min:
                break
            print(m[0],m[1])
            self.topsers.append(m[0])
        return len(self.topsers) 
    

    def getMiners(self):
        self.uminers={}
        try:
            r=requests.get('https://server.duinocoin.com:5000/miners?username='+self.username)
            jdic=json.loads(r.text)
            if jdic['success']==True:
                    self.uminers=jdic['result']
                    return len(self.uminers)
            else:
                print('*** getMiners for',self.username,'success not true')
                return 99
        except Exception as inst:
            print ("*** getMiners Exception "+str(inst))
            return 99

    def getHashTotal(self):
        hash=0;
        for m in self.uminers:
            hash+=m['hashrate']
        return round(hash)

    def switchUser(self,n):
        try:
            self.username=self.users[n]
            print (" Username is ",self.username)
            return True
        except Exception as inst:
            print ("*** switchUser exception "+str(inst))
            print ("to use provide privusers.py with")
            print ("users=['user0','user1','user2']")
            return False
        
    def showUsers(self):
        try:
            print(" Friends and Foes:")
            n=0
            for u in self.users:
                print ("{:2d}u ".format(n),u)
                n+=1
        except Exception as inst:
            print ("*** showUsers exception "+str(inst))
            print ("to use provide privusers.py with")
            print ("users=['user0','user1','user2']")
    
    def switchTopser(self,n):
        try:
            self.username=self.topsers[n]
            print (" Username is ",self.username)
            return True
        except Exception as inst:
            print ("*** switchTopser exception "+str(inst))
            return False
    
    def showTopsers(self):
        try:
            print(" Top friends of mining:")
            n=0
            for u in self.topsers:
                print ("{:2d}t ".format(n),u)
                n+=1
        except Exception as inst:
            print ("** swhowTopsers exception "+str(inst))
    



