# -*- coding: utf-8 -*-
from serial import *
from bitstring import *
import numpy as np #sudo apt install --no-install-recommends python2.7-minimal python2.7  #sudo apt install python-numpy python-scipy
import sys,argparse,binascii,struct,io
from datetime import datetime

ser = Serial(port='/dev/ttyAMA0',baudrate=38400,timeout = 0.5) #IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

np.set_printoptions(precision=3,suppress=True) #fixes weird printout

windowsize = 40
window = np.full([windowsize, 8], np.nan) #creates window, second val is # columns

def report(hex):
	power_factor,phase,P_real,P_reac,P_app,Vrms,Irms = decode(hex)
	now = int(datetime.now().second) + round(datetime.now().microsecond / 1e+6, 4)
	print('     Time', 'PF','Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
	val = [now,round(power_factor,2),round(phase,2),round(P_real,2),round(P_reac,2),round(P_app,2),round(Vrms,2),round(Irms,2)]
	# print(val)
	return val

def convert2bits(payload):
    """convert decimal string back to bitstream and to hex string """
    bits = ''.join([chr(int(b)) for b in payload.split()])
    hex = '0x'+binascii.hexlify(bits)
    return hex

def decode(hex):
    """decode hex string to attributes"""
    a = BitStream(hex)
    return a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32"), \
           a.read("floatle:32")

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

#TODO REFINE THIS USING PERONA OR CANNY FILTER?
def detect_event(window,index=2,threshold=10): #threshold is important
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
            # print('buffer:',ser.in_waiting,'line:',sio.readline())
            # now = round((datetime.now().second + datetime.now().microsecond) / 1e4, 2)
            # print(now)
            if(ser.in_waiting > 0):
                line = sio.readline()
                #print('len:', len(line), line)

				#TODO REMOVE RADIO 433MHZ PRINTOUT

                if len(line) > 100: #checks if line is what we expect
                    if len(line) > 2:
                        if line[1] == 'E': ser.write('1q')  # suppress bad packets
                        if line[:2] == 'OK':
                            #print(line[5:-6]) #print raw packet
                            snapshot = report(convert2bits(line[5:-6]))
                            window = shift_window(window,-1,snapshot) #rebuilds window
                            print(window)
                            print('delta T:',round(window[-1][0]-window[-2][0],4))
                            if detect_event(window):#begin classification
                                pass

        except SerialException:
            print('SerialException...is someone else already connected?')
        except ReadError:
            print('FIX ME: ReadError')#..reading off the end of the data. Tried to read 32 bits when only 16 available.')
            #print('maybe this can be fixed by splitting the packet into two and running report 2X?')
        except ValueError:
            print('VALUE ERROR',line[5:-6]) #print raw packet
        except KeyboardInterrupt:
            ser.close()
            sys.exit()  # exits without writing file

#log
# serial.serialutil.SerialException: device reports readiness to read but returned no data (device disconnected or multiple access on port?)

#TODO CONFIRM THAT WE DON'T GET THESE ERROR ANYMORE (I THINK ITS FIXED)
#('VALUE ERROR', u'222 151 143 61 125 245 171 66 181 88 224 61 236 125 199 63 234 251 199 63 143 153 216 66 15OK 5 142 219 73 187 91 90 180 66 40 243 84 186 117 8 135 62 159 8 135 62 175 12 217 66 27 68 31 59')
#('VALUE ERROR', u'115 72 34 60 109 221 178 6642 59 201 209 134 62 122 211 134 62 66 183 216 66 27 68 31 59')
# ('VALUE ERROR', u'86 OK 5 255 242 252 62 224 146 113 66 42 43 58 66 120 208 163 66 250 105 188 66 12 210 216 66 221 117 94 63')
#('VALUE ERROR', u'48 244 22 188 72 14 181 66 41 232 148 187 144 132 252 62 79 135 252 62 91 57 217 66 E i5 g210 @ 433 MHz q1 U')
#('VALUE ERROR', u'237 75 36 187 139 73 180 66 203 215 160 186 45 158 250 62 97 158 250 62 200 148 215OK 5 125 17 21 187 185 66 180 66 46 1 146 186 234 188 250 62 20 189 250 62 48 175 215 66 165 205 148 59')
#('VALUE ERROR', u'201 64 36 60 230 217 178 66 82 132 160 59 16 42 250 62 72 45 250 62OK 5 10 230 25 60 112 236 178 66 122 60 150 59 154 229 249 62 109 232 249 62 68 248 214 66 165 205 148 59')
# ('VALUE ERROR', u'214 251 253 62 111 10 113 66 121 184 71 66 159 202 174 66 92 78 201 66 163 202 216 OK 5 100 164 253 62 129 55 113 66 91 251 56 66 123 46 162 66 146 179 186 66 129 225 216 66 135 96 92 63')
#print('FIX ME: ReadError..reading off the end of the data. Tried to read 32 bits when only 16 available.')
