# -*- coding: utf-8 -*-
from serial import *
from bitstring import *
import \
    numpy as np  # sudo apt install --no-install-recommends python2.7-minimal python2.7  #sudo apt install python-numpy python-scipy
import sys, argparse, binascii, struct, io
from datetime import datetime
from sklearn.svm import SVC
import tensorflow as tf
import os
import pickle
import matplotlib.pyplot as plt                  # plots

# import keras

from sklearn import preprocessing
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))

tf.enable_eager_execution()

model_path = '/home/pi/DEV/lq_svc_model_1.sav'
model = pickle.load(open(model_path, 'rb'))

ser = Serial(port='/dev/ttyAMA0', baudrate=38400, timeout=0.005)  # IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

np.set_printoptions(precision=3, suppress=True)  # fixes weird printout

windowsize = 46
# real_p = []
# app_p = []
# meas_v = []
window = np.full([windowsize, 8], np.nan)  # creates window, second val is # columns

appliance_dict_1 = {0: 'heatpad', 1: 'hairdryer', 2: 'kettle', 3: 'inductioncooktop', 4: 'cell', 5: 'LEDpicture', 6: 'laptop'}


def make3D(array, n):  # adds channels to array to simulate an image
    return (np.stack((array,) * n, axis=-1))


def convert_str_to_int(str_list, keys):  # converts labels from string to integer
    list_int = []
    for i in str_list:
        list_int.append(appliance_dict_1[i])
    return list_int


def convert_int_to_str(integer, keys):
    for appliance, index in keys.items():
        if index == integer:
            # print(integer,appliance)
            return appliance


def report(hex,time):
    power_factor, phase, P_real, P_reac, P_app, Vrms, Irms = decode(hex)
    # print('     Time', 'PF','Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
    val = [time, round(power_factor, 2), round(phase, 2), round(P_real, 2), round(P_reac, 2), round(P_app, 2),
           round(Vrms, 2), round(Irms, 2)]

    # real_p.append(P_real)
    # app_p.append(P_app)
    # meas_v.append(Vrms)
    # print(val)
    return val


def convert2bits(payload):
    """convert decimal string back to bitstream and to hex string """
    bits = ''.join([chr(int(b)) for b in payload.split()])
    hex = '0x' + binascii.hexlify(bits)
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


# TODO REFINE OFF THRESHOLD
def detect_on(window, index=3, threshold=10):  # threshold is important
    """ listens for a change in active power and returns boolean for event detection
    can use Active/real(P), Apparent(S), and Reactive (Q)(worst..high SNR)"""
    prev_avg = np.average([window[-2][index], window[-3][index], window[-4][index]])
    if window[-1][index] - prev_avg > threshold:  # if power change > average of last two readings
        print('------------ON------------')  # ,window[-1][index])
        return True
    else:
        return False


# TODO REFINE OFF THRESHOLD
def detect_off(window, index=3, threshold=20):  # threshold is important
    """ listens for a change in active power and returns boolean for event detection
    can use Active/real(P), Apparent(S), and Reactive (Q)(worst..high SNR)"""
    prev_avg = np.average([window[-2][index], window[-3][index], window[-4][index]])
    if window[-1][index] - prev_avg < -1 * threshold:  # if power change > average of last two readings
        print('------------OFF------------')
        return True
    else:
        return False


def track_consumption(snapshot, index=3, power=0):
    # window[-1][index]
    return snapshot[index]


# running tally for device consumption
hairdryer = []
laptop = []


def classify_device(window):
    print("Shape before", window.shape)
    # print("before normalization", window)
    # window_padded = tf.keras.preprocessing.sequence.pad_sequences(np.asarray(window), value=0, maxlen=50) #pads length to 50
    # print("Shape after padding", window_padded.shape)
    # print("Window after padding", window_padded[0])
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
    window_normalized = min_max_scaler.fit_transform(window)
    # print('Shape after scale:', window_normalized.shape)
    # print("Window after scale", window_normalized[0])
    window_np = np.array(window_normalized)
    # print("shape after np:", window_np.shape)
    # print('window after np', window_np)
    nx, ny = window_np.shape
    data = window_np.reshape(nx*ny)
    # print('Shape after reshape 1:', data.shape)
    # print("Window after reshape 1:", data)
    data_re = data.reshape(1,-1)
    # print('Shape after reshape 2:', data_re.shape)
    # print("Window after reshape 2:", data_re)
    guess = model.predict(data_re)
    # print("after normalization", window_normalized[0])
    #
    # print("make3D shape before", window_3D.shape)
    # print("shape before feeding in", data.shape)
    # print('input to predict:', data.shape, type(data))

    # window_3D = make3D(window, 3)
    # data = window_3D[tf.newaxis, ...]
    # guess = model.predict(data, verbose=1)
    # print('guess:', guess)
    return guess

window_buffer = 3

if __name__ == '__main__':

    count = 0
    energy = 0
    flag = False
    print('Ready to detect')
    start = datetime.now()
    while ser.is_open:
        try:
            # print('buffer:',ser.in_waiting,'line:',sio.readline())
            # now = round((datetime.now().second + datetime.now().microsecond) / 1e4, 2)
            if (ser.in_waiting > 0):
                # print('Got into ser is waiting')
                line = sio.readline()
                if len(line) > 100:  # checks if line is what we expect
                    # print('line length is greater than 100')
                    if line[1] == 'E':
                        ser.write('1q')  # suppress bad packets
                    elif line[:2] == 'OK':
                        # print(line[5:-6]) #print raw packet
                        now = int((datetime.now() - start).seconds) + round((datetime.now() - start).microseconds / 1e+6, 4)
                        snapshot = report(convert2bits(line[5:-6]), now)
                        # print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                        # print(snapshot)
                        window = shift_window(window, -1, snapshot)  # rebuilds window
                        # TODO FIX DELTA_T TIME INCREMENTS?
                        deltaT = round(window[-1][0] - window[-2][0], 4)
                        if deltaT <= 0:
                            deltaT = round(window[-2][0] - window[-3][0], 4)
                        # print(window)
                        # print("--Averages--",round(window.mean(axis=0)[1],2),round(window.mean(axis=0)[2],2),round(window.mean(axis=0)[3],2),round(window.mean(axis=0)[4],2),round(window.mean(axis=0)[5],2),round(window.mean(axis=0)[6],2),round(window.mean(axis=0)[7],2))

                        if detect_on(window):  # begin classification
                            # print('detected on')
                            # print(window.shape)
                            if flag == False:
                                start = datetime.now()
                            flag = True

                        if flag == True:
                            count += 1
                            power = snapshot[3]  # P_real
                            energy += (power * deltaT) / 3600
                            # print('energy:',round(energy,3),'power:',power,'deltaT',deltaT)

                        if count == windowsize - window_buffer:
                            print('----------------------------------------------------')
                            print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                            print(window)
                            prediction = classify_device(window)  # classifies current device
                            print('----------------APPLIANCE-----------------')
                            print(str(prediction[0]).upper())
                            print('----------------------------------------------------')
                            # plt.figure(figsize=(16,13))
                            # plt.text(0.5, 0.7, prediction[0], size=100,
                            #          ha="center", va="center",
                            #          bbox=dict(boxstyle="round",
                            #                    ec=(1., 0.5, 0.5),
                            #                    fc=(1., 0.8, 0.8),
                            #                    )
                            #          )
                            # plt.axis('off')
                            # plt.show()


                            # #saving for debug
                            # app_name = raw_input("description?")
                            # filename = 'window_' + app_name
                            # print('saving as:',filename)

                            # with open(filename, 'wb') as f:
                            #     np.savetxt(f, window, fmt='%-7.8f', delimiter=',')
                            #     print('written to file')
                            sys.exit()

                            # TODO ADD POWER COUNT TO RUNNING TALLY PER DEVICE

                            # print('count:',count)
                        # if detect_off(window):
                        #     print(window)
                        #     print(window.shape)
                        #     print('TOTAL CONSUMPTION:',energy,'W*h')
                        #     sys.exit()
                    else:
                        print("did not get OK as start")
                        print(line[:2])



        except SerialException:
            print('SerialException...is someone else already connected?')
        except KeyboardInterrupt:
            ser.close()
            sys.exit()  # exits without writing file
        except ReadError:
            print(
                'FIX ME: ReadError')  # ..reading off the end of the data. Tried to read 32 bits when only 16 available.')
        # except ValueError:
            # print('VALUE ERROR')#, line[5:-6])  # print raw packet

# log
# serial.serialutil.SerialException: device reports readiness to read but returned no data (device disconnected or multiple access on port?)
# ('VALUE ERROR', u'222 151 143 61 125 245 171 66 181 88 224 61 236 125 199 63 234 251 199 63 143 153 216 66 15OK 5 142 219 73 187 91 90 180 66 40 243 84 186 117 8 135 62 159 8 135 62 175 12 217 66 27 68 31 59')
# ('VALUE ERROR', u'115 72 34 60 109 221 178 6642 59 201 209 134 62 122 211 134 62 66 183 216 66 27 68 31 59')
# ('VALUE ERROR', u'86 OK 5 255 242 252 62 224 146 113 66 42 43 58 66 120 208 163 66 250 105 188 66 12 210 216 66 221 117 94 63')
# ('VALUE ERROR', u'48 244 22 188 72 14 181 66 41 232 148 187 144 132 252 62 79 135 252 62 91 57 217 66 E i5 g210 @ 433 MHz q1 U')
# ('VALUE ERROR', u'237 75 36 187 139 73 180 66 203 215 160 186 45 158 250 62 97 158 250 62 200 148 215OK 5 125 17 21 187 185 66 180 66 46 1 146 186 234 188 250 62 20 189 250 62 48 175 215 66 165 205 148 59')
# ('VALUE ERROR', u'201 64 36 60 230 217 178 66 82 132 160 59 16 42 250 62 72 45 250 62OK 5 10 230 25 60 112 236 178 66 122 60 150 59 154 229 249 62 109 232 249 62 68 248 214 66 165 205 148 59')
# ('VALUE ERROR', u'214 251 253 62 111 10 113 66 121 184 71 66 159 202 174 66 92 78 201 66 163 202 216 OK 5 100 164 253 62 129 55 113 66 91 251 56 66 123 46 162 66 146 179 186 66 129 225 216 66 135 96 92 63')
# print('FIX ME: ReadError..reading off the end of the data. Tried to read 32 bits when only 16 available.')
