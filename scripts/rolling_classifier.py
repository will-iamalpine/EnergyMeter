# -*- coding: utf-8 -*-
from serial import *
from bitstring import *
import numpy as np  # sudo apt install --no-install-recommends python2.7-minimal python2.7  #sudo apt install python-numpy python-scipy
from datetime import datetime
import helper_functions as hf
import os,sys, argparse, binascii, struct, io
import warnings, time
warnings.filterwarnings("ignore")

np.set_printoptions(precision=3, suppress=True)  # fixes weird printout

#---------------------------------ML model setup----------------------------------------
import tensorflow as tf
tf.enable_eager_execution()
# import keras
appliance_dict = {0: 'cell', 1: 'desklamp', 2: 'fan', 3: 'kettle', 4: 'laptop', 5: 'monitor', 6: 'none', 7: 'sadlamp'} #N.B. update this with each model!
model_path = '/home/pi/DEV/wb_model_2.h5'
model = tf.keras.models.load_model(model_path)

storage_path = '/home/pi/DEV/data_train' #where files are written

ser = Serial(port='/dev/ttyAMA0', baudrate=38400, timeout=0.005)  # IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

#--------------------------------window----------------------------------------
windowsize = 40 #this must be consistent with training & model dimensions
window_buffer = 3 #buffer to show startup sequence
window = np.full([windowsize, 8], np.nan)  # initializes window, second val is # columns


if __name__ == '__main__':

    count = 0 #counter for building rolling window. Increments when flag = true
    # energy = 0
    #TODO handle multiple appliance operation
    flag = False #state counter for device being on/off. Can only work with one appliance currently
    print('Ready to detect')
    start = datetime.now()
    while ser.is_open:
        try:
            # print('buffer:',ser.in_waiting,'line:',sio.readline())
            # now = round((datetime.now().second + datetime.now().microsecond) / 1e4, 2)
            if (ser.in_waiting > 0):
                line = sio.readline()
                # print(len(line),'line:',line)
                if len(line) > 100:  # checks if line is what we expect
                    if line[1] == 'E':
                        ser.write('1q')  # suppress bad packets
                    elif line[:2] == 'OK':
                        now = int((datetime.now() - start).seconds) + round((datetime.now() - start).microseconds / 1e+6, 4)
                        hex_stream = hf.convert2bits(line[5:-6])  #trims excess packet info
                        hex_attrs = BitStream(hex_stream)
                        snapshot = hf.report(hex_attrs, now)
                        window = hf.shift_window(window, -1, snapshot)  # rebuilds window
                        # print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                        # print("snapshot",snapshot)
                        # print(line[5:-6]) #debug print raw packet
                        # print("hex_stream", hex_stream) #debug print raw hex
                        # print('hex_attrs:', hex_attrs) #debug print attributes
                        # print(window)

                        # TODO refine time increment counter for appliance-level consumption tracking
                        #for power tracking
                        # deltaT = round(window[-1][0] - window[-2][0], 4)
                        # if deltaT <= 0:
                        #     deltaT = round(window[-2][0] - window[-3][0], 4)
                        # print(window)
                        # print("--Averages--",round(window.mean(axis=0)[1],2),round(window.mean(axis=0)[2],2),round(window.mean(axis=0)[3],2),round(window.mean(axis=0)[4],2),round(window.mean(axis=0)[5],2),round(window.mean(axis=0)[6],2),round(window.mean(axis=0)[7],2))

                        if hf.detect_on(window,3,4):  # begin classification
                            if flag == False:
                                print('------------ON------------')
                                start = datetime.now()
                            flag = True

                        if flag == True:
                            count += 1 #increments counter to build window once state is set

                        if count == windowsize - window_buffer: #ready to classify
                            print('----------------------------------------------------')
                            print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                            window = hf.reset_clock(window)
                            print(window)

                            prediction = hf.classify_device(window, model)  # classifies current device
                            # print('prediction:', prediction, type(prediction), prediction.shape)
                            device = tf.argmax(prediction, axis=-1).numpy()
                            print('guess:', device, appliance_dict.get(device[0]))
                            for j in range(0, len(appliance_dict)):
                                print(('guesses: %.2f%% %s' % (100 * prediction[0, j], appliance_dict.get(j))))

                            time.sleep(0.5)
                            count = 0 #reset window counter
                            flag = False #reset state counter
                            window = np.full([windowsize, 8], np.nan) #resets window
                            print('ready to detect')

                    else:
                        print("Packet Error: did not get OK as start...reading next line")
                        # print(line[:2])

        except SerialException:
            print('SerialException...is someone else already connected?')
        except ReadError:
            print('ReadError')
        except ValueError:
            print('ValueError')
        except KeyboardInterrupt:
            ser.close()
            sys.exit()  # exits without writing file
