# -*- coding: utf-8 -*-
import os
import sys
# just want to detect keypress...
# Windows
if os.name == 'nt':
    import msvcrt
# Posix (Linux, OS X)
else:
    import termios
    import atexit
    from select import select


class KBHit:

    def __init__(self):
        if os.name == 'nt':
            pass        
        else:    
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)    
            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)    
            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)
        
    def set_normal_term(self):
        if os.name == 'nt':
            pass       
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        if os.name == 'nt':
            return msvcrt.getch().decode('ascii')        
        else:
            return sys.stdin.read(1)
                        
    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()        
        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []

    def forgetch(self):  #I HATE PYTHON
        try:
            self.getch()
        except:
            pass         
