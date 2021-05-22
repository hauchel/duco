# -*- coding: utf-8 -*-
# transfer duco performance to database
import MySQLdb as mdb
import time

class todb():
    
    def __init__(self):
        self.db = mdb.connect(host='localhost',user='root', password='', database='duco')
        self.cs= self.db.cursor()
        self.verbose=False
        self.tab="games"
        #self.verbose=True
     
    def zeit(self):
        return time.strftime("'%Y-%m-%d  %H:%M:%S'", time.localtime())
        #return time.strftime("'%Y %b %d  %H:%M:%S'", time.localtime())
    def say(self,s):
        if self.verbose:
            print (str(s))

    def logge(self,text,prio=5):
        t="insert into log (Zeit,Prio,Text) values ("
        t+=self.zeit()+","+str(prio)+",'"+text+"')"
        self.execc(t)
        print (">"+text)

    def fetch1(self,query):
        self.say ("Fetch1: "+query)     
        self.cs.execute(query)
        result = self.cs.fetchone()
        self.say ("answer: %s" % str(result))
        self.db.commit()
        return result

    def fetch99(self,query):
        self.say ("Fetch99: "+query)     
        self.cs.execute(query)
        result = self.cs.fetchall()
        self.say ("answer: %s" % str(result))
        self.db.commit()
        return result
    
    def execc(self,query):
        self.say ("execc: "+query) 
        try:
            tmp=self.cs.execute(query)
        except Exception as inst:
            print ("ldb exec Exception "+str(inst)   )
            tmp="kaputt"                         
        self.db.commit()
        return tmp

    def getManyOne(self,query):
        #returns on col as list
        tmp=self.fetch99(query)
        w=[]
        for t in tmp:
            ts=str(t[0])
            w.append(ts)
        return w

    def getDict(self,query):
        #returns dict, col 0 is key
        tmp=self.fetch99(query)
        w={}
        for t in tmp:
            w[t[0]]=t[1]
        return w

    def getDictNum(self,query):
        tmp=self.fetch99(query)
        w={}
        for t in tmp:
            if t[1] is None:
                w[t[0]]=0
            else:
                w[t[0]]=t[1]
        return w

    def insertPrime(self,game,datei,algo,feld):
        t="insert into "+ self.tab+" (datei,game,algo,feld) values ("
        t+=str(datei)+","+str(game)+",'"+algo+"',"
        t+="'"+feld+"');"
        self.execc(t)    

    def readFile(self,myName,myNum):
        fil = open(myName, 'r')
        count=0
        while True:
            count += 1
            line = fil.readline().strip()
            if not line:
                break
            print("Line{}: {}".format(count, line))
            self.insertGame(count,myNum,'a',line)
        fil.close()


if __name__ == "__main__":
    k=todb()  
    k.verbose=True

    if 0:
        k.readFile('top95.txt',4)
    if 1:
        k.readFile('kudok.txt',1)

    
    if 0:
        k.insertGame(4711,2,'a','7862347864866')
