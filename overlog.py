#!/usr/bin/env python
# collect logging from all ESPs
#from __future__ import print_function

import sys
import select
import struct
try:
    import usocket as socket
except ImportError:
    import socket
import websocket_helper

from colorama import init
init()

from kbhit import KBHit
kb = KBHit()

# Define to 1 to use builtin "uwebsocket" module of MicroPython
USE_BUILTIN_UWEBSOCKET = 0
DEBUG = 1

WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2
WEBREPL_GET_VER  = 3


def debugmsg(msg):
    if DEBUG:
        print(msg)


class websocket:

    def __init__(self, s):
        self.s = s
        self.buf = b""

    def write(self, data):
        l = len(data)
        if l < 126:
            # TODO: hardcoded "binary" type
            hdr = struct.pack(">BB", 0x82, l)
        else:
            hdr = struct.pack(">BBH", 0x82, 126, l)
        self.s.send(hdr)
        self.s.send(data)

    def recvexactly(self, sz):
        res = b""
        while sz:
            data = self.s.recv(sz)
            if not data:
                break
            res += data
            sz -= len(data)
        return res
    
    def read(self, size, text_ok=False):
        if not self.buf:
            while True:
                hdr = self.recvexactly(2)
                assert len(hdr) == 2
                fl, sz = struct.unpack(">BB", hdr)
                if sz == 126:
                    hdr = self.recvexactly(2)
                    assert len(hdr) == 2
                    (sz,) = struct.unpack(">H", hdr)
                if fl == 0x82:
                    break
                if text_ok and fl == 0x81:
                    break
                debugmsg("Got unexpected websocket record of type %x, skipping it" % fl)
                while sz:
                    skip = self.s.recv(sz)
                    debugmsg("Skip data: %s" % skip)
                    sz -= len(skip)
            data = self.recvexactly(sz)
            assert len(data) == sz
            self.buf = data

        d = self.buf[:size]
        self.buf = self.buf[size:]
        #assert len(d) == size, len(d)
        return d

def login(ws, passwd):
    while True:
        c = ws.read(1, text_ok=True)
        if c == b":":
            assert ws.read(1, text_ok=True) == b" "
            break
    ws.write(passwd.encode("utf-8") + b"\r")

def read_resp(ws):
    data = ws.read(4)
    sig, code = struct.unpack("<2sH", data)
    assert sig == b"WB"
    return code


def send_req(ws, op, sz=0, fname=b""):
    rec = struct.pack(WEBREPL_REQ_S, b"WA", op, 0, 0, sz, len(fname), fname)
    debugmsg("%r %d" % (rec, len(rec)))
    ws.write(rec)


def get_ver(ws):
    send_req(ws, WEBREPL_GET_VER)
    d = ws.read(3)
    d = struct.unpack("<BBB", d)
    return d


def error(msg):
    print(msg)
    sys.exit(1)

class clog:
    def __init__(self,host,port,sladi):    
        print ("Init ",host)
        self.host=host
        self.port=port
        self.slas=slas
        self.verbose=True
        
    def connect(self):  
        self.soc= socket.socket()
        ai = socket.getaddrinfo(self.host, self.port)
        addr = ai[0][4]
        print ("Addr",str(ai))
        self.soc.connect(addr)
        websocket_helper.client_handshake(self.soc)
        self.ws = websocket(self.soc)
        login(self.ws,'p')
        print("Remote WebREPL version:", get_ver(self.ws))
    
    def close(self):
        print("Closing")
        self.soc.close()
        
    def slect(self):
        readable,writable,exception = select.select([self.soc],[],[],0)
        return len(readable)
        
    def read(self):
        print("Reading")
        if self.slect()>0:
            b = self.soc.recv(100)
            # scan to remove all control info
            ba=bytearray(0)
            skip=False
            for i in range(0,len(b)):
                if skip:
                    skip=False
                elif b[i] == 129:
                    skip=True
                elif b[i]==13:
                    pass
                else:
                   ba.append(b[i])
            return ba.decode()
        else:
            return ""
        
mycons=[]

def get_config():
    global mycons
    conf=open("conflog.txt",'r')
    lin=1
    prev=0;
    slali=dict()
    for l in conf.readlines():
        s=l.rstrip().split(" ")
        if len(s)>1: # host slave, start conf when all slaves known
            if lin==1:
                prev=s[0]
            if prev != s[0]:
                print ("New",prev)
                con=clog('192.168.178.'+str(prev),8266,slali)
                mycons.append(con)
                slali=dict()
                prev=s[0]
            slali[s[1]]=lin
            lin+=1
            print (prev+" >"+s[0]+":"+s[1]+"<",slali)
            
    print ("New",prev)
    con=clog('192.168.178.'+str(prev),8266,slali)
    mycons.append(con)
        
		
def interpret():
	pass
    
         
     
def menu():   
    inpAkt=False
    inp=0
    myc=0
    #
    #query()
    # here after keypress 
    while True:
        if not inpAkt: print(myc,"L>",end="",flush=True)
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
                if ch=="c":
                    mycons[myc].connect()
                elif ch=="d":
                     mycons[myc].close()
                elif ch=="g":
                    get_config()					
                elif ch=="r":
                     mycons[myc].read()
                elif ch=="s":
                     mycons[myc].slect()
                elif ch=="t":
                     myc=inp                   
                elif ch=="u":
                    pass
                elif ch=="x":
                    for cl in mycons:
                        cl.close()
                    return
                else:
                    print("else "+str(ord(ch)))
            except Exception as inst:
                print ("menu Exception "+str(inst))
                raise  #to ease fix
                

menu()