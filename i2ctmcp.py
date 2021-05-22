import machine
from machine import I2C
import sys
class i2ct():
    def __init__(self):
        self.pinSDA=machine.Pin(4)
        self.pinSCL=machine.Pin(5)
        self.con=I2C(scl=self.pinSCL, sda=self.pinSDA)
        self.inaAddress=64
        self.mcpAddress=96
        self.inp=0
        self.inpAkt=False
        #self.config_ina()
    
    def to_bytes(self, register_value):
        return bytearray([(register_value >> 8) & 0xFF, register_value & 0xFF])
	
    def tip(self):
        print("INA Register 0 config 1 Shunt 2 Bus 3 Power 4 Current 5 Calib")
        print("default brng  1 gain  3 badc  3 sadc  3 mode  7 -> calibrate 4096")

    def config_ina(self):
        # default brng  1 gain  3 badc  3 sadc  3 mode  7 -> calibrate 4096
        v=self.read_ina(0,False)
        brng=(v>>13)&1
        gain=(v>>11)&3
        badc=(v>>7)&15
        sadc=(v>>3)&15
        mode=v&7
        print("brng {:2d} gain {:2d} badc {:2d} sadc {:2d} mode {:2d}".format(brng,gain,badc,sadc,mode))
        self.write_ina(5,4096)
        

    def volt(self):
        return (self.read_ina(2)>>3)*4
    
    def read_ina(self, register, negative_value_supported=True):
        register_bytes = self.con.readfrom_mem(self.inaAddress, register, 2)
        register_value = int.from_bytes(register_bytes, 'big')
        if negative_value_supported:
            # Two's compliment
            if register_value > 32767:
                register_value -= 65536
        return register_value
    
    def write_ina(self, register, register_value):
        register_bytes = self.to_bytes(register_value)
        self.con.writeto_mem(self.inaAddress, register, register_bytes)

    def write_mcp(self, register_value):
        register_bytes = self.to_bytes(register_value)
        self.con.writeto(self.mcpAddress, register_bytes)

    def getch(self):
        while True:
            ch= sys.stdin.read(1)     
            if ch is not None:
                print (ch,end='')
                if (ch>='0') and (ch<='9'):
                    if (self.inpAkt):
                        self.inp=self.inp*10+ord(ch)-ord('0')
                    else:
                        self.inpAkt=True
                        self.inp=ord(ch)-ord('0')
                else:
                    self.inpAkt=False
                    return ch
        
    def menu(self):   
        while True:
            print("M>",end="")
            tmp=self.getch()
            try:
                if tmp=="a":
                    self.write_mcp(self.inp)
                    print("Aut="+str(self.inp))
                elif tmp=="b":
                    print("1bbb")
                elif tmp=="i":
                    print(self.read_ina((4)))
                elif tmp=="n":
                    print(self.inp,end='')
                    self.inpAkt=True #cont. num
                elif tmp=="u":
                    print(self.volt())
                elif tmp=="x":
                    return
                else:
                    print("a,i,n,u,x")
            except Exception as inst:
                print ("menu1 Exception "+str(inst))
                return


