import serial
import sys
import struct
import time
import os
import threading

class senser:
    ser=None
    #Acceleration
    ax=0
    ay=0
    az=0
    #Angular Acceleration
    wx=0
    wy=0
    wz=0
    #Temperature
    t=0
    #Angle
    dx=0
    dy=0
    dz=0
    #system time
    st=0
    to=0
    #
    typ=0
    lbuf=[]
    fa=None     #record acceleration
    fw=None     #record angular velocity
    fd=None     #record angle
    def __init__(self,port,string):
        try:
            self.ser = serial.Serial(port,115200,timeout=1)
        except serial.SerialException:
            print "Failed to open port "+port+", exit..."
            sys.exit()
            
        path="gyro/%s"%string
        print path
        try:
            os.mkdir("gyro")
        except:
            try:
                os.mkdir(path)
            except:
                pass
        try:
            os.mkdir(path)
        except:
            pass
        self.fa=open("%s/Acceleration.txt"%path,'w+')
        self.fw=open("%s/Angular Velocity.txt"%path,'w+')
        self.fd=open("%s/Angle.txt"%path,'w+')

        print >> self.fa, "Time\tAx\tAy\tAz\tTemperature"
        print >> self.fw, "Time\tWx\tWy\tWz\tTemperature"
        print >> self.fd, "Time\tDx\tDy\tDz\tTemperature"

    def convert(self,h,l):
        ret=h<<8|l
        if ret&0x8000:
            if ret==0x8000:
                ret=0-0x8000
            else:
                ret=ret-0x10000
        return ret

    def decode(self):
        self.st=time.time()-self.to
        if self.typ==0x51:
            ax=self.convert(self.lbuf[1],self.lbuf[0])/32768.0*16*9.8
            ay=self.convert(self.lbuf[3],self.lbuf[2])/32768.0*16*9.8
            az=self.convert(self.lbuf[5],self.lbuf[4])/32768.0*16*9.8
            t=self.convert(self.lbuf[7],self.lbuf[6])/340.0+36.53
            print>>self.fa, "%.3f\t%.3f\t%.3f\t%.3f\t%.3f" %(self.st,ax,ay,az,t)
        elif self.typ==0x52:
            wx=self.convert(self.lbuf[1],self.lbuf[0])/32768.0*2000
            wy=self.convert(self.lbuf[3],self.lbuf[2])/32768.0*2000
            wz=self.convert(self.lbuf[5],self.lbuf[4])/32768.0*2000
            t=self.convert(self.lbuf[7],self.lbuf[6])/340.0+36.53
            print>>self.fw, "%.3f\t%.3f\t%.3f\t%.3f\t%.3f" %(self.st,wx,wy,wz,t)
        elif self.typ==0x53:
            dx=self.convert(self.lbuf[1],self.lbuf[0])/32768.0*180
            dy=self.convert(self.lbuf[3],self.lbuf[2])/32768.0*180
            dz=self.convert(self.lbuf[5],self.lbuf[4])/32768.0*180
            t=self.convert(self.lbuf[7],self.lbuf[6])/340.0+36.53
            print>>self.fd, "%.3f\t%.3f\t%.3f\t%.3f\t%.3f" %(self.st,dx,dy,dz,t)
        else:
            return

    def collect(self,event):
        count=-1
        try:
            self.to=time.time()
            self.st=time.time()-self.to
            while (not event.isSet()):
                buf=self.ser.read()
                num=struct.unpack("B",buf)[0]
                if count==-1 and num==0x55:
                    count=0
                    print count
                elif count==0:
                    if num==0x51 or num==0x52 or num==0x53:
                        self.typ=num
                        count+=1
                        self.lbuf=[]
                    else:
                        count=-1
                elif count>=1 and count<10:
                    count+=1
                    if count==10:
                        SUM=0x55+self.typ
                        for n in self.lbuf:
                            SUM+=n
                        if SUM&0xFF==num:
                            self.decode()
                    else:
                        self.lbuf.append(num)
                elif count==10:
                    if num==0x55:
                        count=0
                    else:
                        count=-1
        except:
            self.ser.close()
            self.fa.close()
            self.fw.close()
            self.fd.close()

if __name__=="__main__":
    sen = senser("com4","w=0")
    event=threading.Event()
    sen.collect(event)
