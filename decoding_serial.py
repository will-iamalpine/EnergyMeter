# -*- coding: utf-8 -*-
from serial import *
from bitstring import *
import numpy as np #sudo apt install --no-install-recommends python2.7-minimal python2.7  #sudo apt install python-numpy python-scipy
import sys,argparse,binascii,struct,io,datetime

ser = Serial(port='/dev/ttyAMA0',baudrate=38400,timeout=4)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

windowsize = 20
window = np.full([windowsize, 7], np.nan) #creates window

DEBUG = False

def convert2bits(payload):
    """convert decimal string back to bitstream and to hex string """
    bits = ''.join([chr(int(b)) for b in payload.split()])
    hex = '0x'+binascii.hexlify(bits)
    return hex

def decode(hex):
    """decode hex string to attributes"""
    a = BitStream(hex)
    return a.read("uintle:16"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32")

def report(hex):
    phase,P_real,P_reac,P_app,Vrms,Irms = decode(hex)
    #print("Phase angle=%d Real power=%d Reactive power=%d Apparent power=%d Vrms=%d Irms=%d" % (phase_angle,power_real,power_reactive,power_apparent,Vrms,Irms))
    now = datetime.datetime.now()
    timestamp = ('%02d:%02d:%02d.%d' % (now.hour, now.minute, now.second, now.microsecond))[:-3]
    #print(timestamp)
    #TODO get timestamp in correct format
    #time = np.datetime64()
    #print(time)
    print(timestamp,'Phase','P_real','P_reac','P_app,','V_rms','I_rms')
    #TODO MAKE SURE PHASE, REACTIVE & APPARENT POWER IS CALIBRATED
    val = [now.second,round(phase,1),round(P_real,1),round(P_reac,1),round(P_app,1),round(Vrms,4),round(Irms,1)]
    #print(val)
    return val

def shift_window(arr, num, fill_value=np.nan):
    """rolling window to listen for events and store in short term memory"""
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result = arr
    return result

#TODO REFINE THIS
def detect_event(window,index=2,threshold=5): #window=np.array
    """ listens for a change in active power and returns boolean for event detection
    can use Active/real(P), Apparent(S), and Reactive (Q)(worst..high SNR)"""
    prev_avg = np.average([window[-2][index],window[-3][index],window[-4][index]])
    if abs(window[-1][index]-prev_avg) > threshold: #if power change > average of last two readings
         print('EVENT DETECTED')
         return True
    else:
        return False



if __name__ == '__main__':
    while ser.is_open:
        try:
            line = sio.readline()
            if len(line) > 0:
                if DEBUG: print("<%s>:%s" % (len(line),line))
                if len(line) > 2:
                    if line[1] == 'E': ser.write('1q')  # suppress bad packets
                    if line[:2] == 'OK':
                        #print(line[5:-6]) #print raw packet
                        snapshot = report(convert2bits(line[5:-6]))
                        window = shift_window(window,-1,snapshot) #rebuilds window
                        print(window)
                        if detect_event(window):
                            pass

        except KeyboardInterrupt:
            ser.close()
            break
