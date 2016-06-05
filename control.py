import serial
import struct
import time
from senser2 import *
import threading
import sys

event = threading.Event()

def senser_func(port,string):
    print "collecting"
    sen=senser(port,string)
    sen.collect(event)

ser=None
delta_r=235.0/2
PI=3.1415926

def getDecodedBytes(n,fmt):
    global ser
    return struct.unpack(fmt,ser.read(n))[0]

def goDirectly(velocity,radius,t):
    global ser
    ser.write(struct.pack(">Bhh",137,velocity,radius))
    time.sleep(t)
    ser.write(struct.pack(">Bhh",137,0,32767))

def goFowardDirectly(velocity,t):
    goDirectly(velocity,32767,t)

def spinDirectly(direction,angular_v,t):
    goDirectly(int(delta_r*angular_v*PI/180.0),direction,t)

def goIndependently(velocity,radius,t):
    global ser
    if radius==32767 or radius==-32768:
        v1=velocity
        v2=velocity
    elif radius==1 or radius==-1:
        v1=velocity
        v2=radius*velocity
    else:
        v1=int(velocity*(radius+delta_r)/radius)
        v2=int(velocity*(radius-delta_r)/radius)
    ser.write(struct.pack(">Bhh",145,v1,v2))
    time.sleep(t)
    ser.write(struct.pack(">Bhh",145,0,0))

def goFowardIndependently(velocity,t):
    goIndependently(velocity,32767,t)

def spinIndependently(direction,angular_v,t):
    goIndependently(int(delta_r*angular_v*PI/180.0),direction,t)

def getDist():
    ser.write(struct.pack(">BB",142,19))
    d=getDecodedBytes(2,">h")
    ser.write(struct.pack(">BB",142,20))
    a=getDecodedBytes(2,">h")
    return (d,a)

port=raw_input("irobot port:")
port2=raw_input("senser port:")
string=None
try:
    ser=serial.Serial(port,baudrate=115200,timeout=1)
except:
    print>>sys.stderr,"Can't open port:%s, exiting..."%port
    sys.exit()
angle0=0.0
angle1=0.0
dist0=0.0
dist1=0.0


#spining
string="spin,w=60,times=1"
thread1=threading.Thread(target=senser_func,args=(port2,string,))
thread1.start()
time.sleep(1)

for i in range(1):
    ser.write(struct.pack(">B",128))
    ser.write(struct.pack(">B",131))
    #(dist0,angle0)=getDist()
    #print "%d:d0=%f\na0=%f\n" %(i,dist0,angle0)
    spinDirectly(1,60,6)
    #(dist1,angle1)=getDist()
    #print "%d:d1=%f\na1=%f\n" %(i,dist1,angle1)
    spinDirectly(-1,60,6)
time.sleep(1)
event.set()
ser.close()
