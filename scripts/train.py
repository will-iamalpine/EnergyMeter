from serial import *
from bitstring import *
import numpy as np  # sudo apt install --no-install-recommends python2.7-minimal python2.7  #sudo apt install python-numpy python-scipy
from datetime import datetime
import helper_functions as hf
import os,sys, argparse, binascii, struct, io, warnings, time
warnings.filterwarnings("ignore")
np.set_printoptions(precision=3, suppress=True)  #human-readable printout setting

#--------------------------------------be sure to collect baseline empty windows--------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--empty', action = "store_true", help = 'collects a baseline window to prevent stray classification (e.g. on/off trailing spikes)') #compiles optional args to list
args = parser.parse_args()

#--------------------------------------serial info--------------------------------------
ser = Serial(port='/dev/ttyAMA0', baudrate=38400, timeout=0.005)  # IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

#--------------------------------------window characteristics--------------------------------------
windowsize = 40 #number of rows in CSV. Be sure to be consistent with array characteristics for classification
window_buffer = 3 #buffer before window is collected. used to show the startup characteristics
window = np.full([windowsize, 8], np.nan)  # initializes window, second val is # columns

# --------------------------------------storage path--------------------------------------
storage_path = '/home/pi/DEV/data_test' #where to put your training dataset
if __name__ == '__main__':

    start = datetime.now() #starts clock
    if args.empty:
        print('\nAutomated collection of empty window. Set run_number logic to stop at desired # of runs\n')
    else:
        print('\nManual window collection mode: switch appliance on, and wait until prompted to save name. '
              'required input format: (appliance class_run #)....e.g. laptop_1, or cell_99'
              'remember to copy/paste and then enter number (e.g. "kettle_") '
              'optional argument separated by "-" as descriptor (e.g. laptop-username_)\n')
    print('\nReady to collect training data...\n')
    count = 0  # counter for building rolling window. Increments when flag = true
    run_number = 1 #only used for empty window collection
    flag = False #for manual collection/event detection
    while ser.is_open:
        if args.empty: #for collecting empty window/baseline comparison
            try:
                # print('buffer:',ser.in_waiting,'line:',sio.readline())
                # now = round((datetime.now().second + datetime.now().microsecond) / 1e4, 2)
                if (ser.in_waiting > 0):
                    line = sio.readline()
                    # print(len(line),'line:',line)
                    if len(line) > 100:  # checks for packet receipt
                        if line[1] == 'E':
                            ser.write('1q')  # suppress bad packets
                        elif line[:2] == 'OK':
                            now = int((datetime.now() - start).seconds) + round((datetime.now() - start).microseconds / 1e+6, 4)
                            hex_stream = hf.convert2bits(line[5:-6])  #trims excess packet info
                            hex_attrs = BitStream(hex_stream)
                            snapshot = hf.report(hex_attrs, now) #current values
                            window = hf.shift_window(window, -1, snapshot)  # rebuilds window
                            count +=1 #increment window counter

                            if count == windowsize:
                                print('----------------------------------------------------')
                                print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                                window = hf.reset_clock(window)
                                print(window[:20]) #sanity check the readings

                                app_name = 'none_'+str(run_number)
                                hf.write_file(window,app_name,storage_path) #saves file to training path
                                time.sleep(0.5)
                                run_number +=1  #increment the run to save in new file
                                print('File saved, clearing window and beginning collection....\n')
                                start = datetime.now() #resets clock
                                window = np.full([windowsize, 8], np.nan) #reset window
                                count = 0 #resets counter
                            if run_number == 101: #100 samples, starting at 1
                                print('Finished collecting empty widows, exiting...')
                                sys.exit()

                        else:
                            print("did not get OK as start, next reading...")
            except SerialException:
                print('SerialException...is someone else already connected?')
            except ReadError:
                print('ReadError')
            except ValueError:
                print('ValueError')
            except KeyboardInterrupt:
                ser.close()
                sys.exit()  # exits without writing file
        else: #the main block for data collection
            try:
                # print('buffer:',ser.in_waiting,'line:',sio.readline()) #debug
                if (ser.in_waiting > 0):
                    line = sio.readline()
                    # print(len(line),'line:',line) #debug
                    if len(line) > 100:  # checks for packet receipt
                        if line[1] == 'E':
                            ser.write('1q')  # suppress bad packets
                        elif line[:2] == 'OK':
                            now = int((datetime.now() - start).seconds) + round((datetime.now() - start).microseconds / 1e+6, 4)
                            hex_stream = hf.convert2bits(line[5:-6])  #trims excess packet info
                            hex_attrs = BitStream(hex_stream)
                            snapshot = hf.report(hex_attrs, now) #current values
                            window = hf.shift_window(window, -1, snapshot)  # rebuilds window
                            ##debug:
                            # print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                            # print("snapshot",snapshot)
                            # print(line[5:-6]) #debug print raw packet
                            # print("hex_stream", hex_stream) #debug print raw hex
                            # print('hex_attrs:', hex_attrs) #debug print attributes
                            # print(window)

                            if hf.detect_on(window,3,4):  # begin classification
                                if flag == False:
                                    print('------------ON------------')
                                    start = datetime.now()
                                flag = True #state detection: appliance is now seen as on
                            if flag == True: #state detection: if appliance is on, increment count
                                count += 1 #increments counter

                            if count == windowsize-window_buffer: #window is populated, label it
                                print('----------------------------------------------------')
                                print('     Time', 'PF', 'Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
                                window = hf.reset_clock(window) #normalizes time value. Could be improved
                                print(window[:20]) #sanity check the readings. you'll learn to notice fluctuations or strange states

                                print('\nTURN OFF DEVICE NOW\n')
                                if (sys.version_info > (3, 0)): # Python 3 text input
                                    print("description? please enter in format of 'appliance-descriptor_run# (e.g. laptop-user_1")
                                    app_name = input()
                                else: # Python 2 text input
                                    print("description? please enter in format of 'appliance-descriptor_run# (e.g. laptop-user_1")
                                    app_name = raw_input()

                                hf.write_file(window,app_name,storage_path) #saves file to training path
                                time.sleep(1) #reduces errant event triggers. sometimes catches the tail end if device isn't turned off quickly enough
                                print('File saved, ready for next sample')
                                start = datetime.now() #reset clock
                                window = np.full([windowsize, 8], np.nan) #reset window
                                count = 0 #reset counter
                                flag = False #reset state (no known appliance active)
                        else:
                            print("did not get OK as start, next reading...")
            except SerialException:
                print('SerialException...is someone else already connected?')
            except ReadError:
                print('ReadError')
            except ValueError:
                print('ValueError')
            except KeyboardInterrupt:
                ser.close()
                sys.exit()  # exits without writing file