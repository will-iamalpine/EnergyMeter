import sys, argparse, binascii, struct, io
from sklearn import preprocessing
import tensorflow as tf
import numpy as np
import os

def convert_str_to_int(str_list, keys):  # converts labels from string to intege
    """"converts string to integer per appliance dictionary"""
    list_int = []
    for i in str_list:
        list_int.append(keys[i])
    return list_int

def convert_int_to_str(integer, keys):
    """"converts integer to string per appliance dictionary"""
    for appliance, index in keys.items():
        if index == integer:
            return appliance

#------------------------------------DATA RESHAPING------------------------------------
def make3D(array, n):  # adds channels to array to simulate an image
    """shapes an array from (50,8) to (50,8,n) for image processing functions"""
    return (np.stack((array,) * n, axis=-1))

def normalize_reshape(array_2d):
    '''input: feature array w/ shape (50,8)
    returns: shape (1,50,8,3) w/features normalized between 0 and 1'''
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))  # for normalizing between 0 and 1
    array_normalized = min_max_scaler.fit_transform(array_2d)
    array_3D = make3D(array_normalized, 3)
    array_4D = array_3D[tf.newaxis,...]
    # print('window.shape',window.shape)
    # print('array_normalized',array_normalized[0][:10)
    # print('array_3D shape', array_3D.shape)
    # print('array_4D shape', array_4D.shape)
    # print(array_4D[0])
    return array_4D

def write_file(array,description, filepath=os.getcwd(),filetype='.csv'):
    """write file to location and prints out confirmation"""
    save_path = os.path.join(filepath,description) + filetype
    with open(save_path, 'wb') as f:
        np.savetxt(f, array, fmt='%-7.8f', delimiter=',')
        print('written to file as', save_path)

#------------------------------------EVENT DETECTION & CLASSIFICATION------------------------------------
# TODO REFINE ON THRESHOLD
def detect_on(window, index=3, threshold=5):  # threshold value is important: power(watts)
    """input: np array
    listens for a change in active power that exceeds threshold
    (can use Active/real(P), Apparent(S), and Reactive (Q)(worst..high SNR))
    index = index of feature to detect. Used P_real @ index 3
    returns: boolean for event detection"""
    prev_avg = np.average([window[-2][index], window[-3][index], window[-4][index]])
    if window[-1][index] - prev_avg > threshold:  # if power change > average of last two readings
        return True
    else:
        return False

# TODO REFINE OFF THRESHOLD
def detect_off(window, index=3, threshold=20):  # threshold is important
    """ listens for a change in active power and returns boolean for event detection
    can use Active/real(P), Apparent(S), and Reactive (Q)(worst..high SNR)"""
    prev_avg = np.average([window[-2][index], window[-3][index], window[-4][index]])
    if window[-1][index] - prev_avg < -1 * threshold:  # if power change > average of last two readings
        return True
    else:
        return False

def classify_device(array,model):
    """input: np feature array w/ shape (40,8), not normalized
     output: tensor array of predictions"""
    reshaped = normalize_reshape(array)
    # cast = tf.cast(reshaped, tf.float32)
    # print('cast to float32')
    return model.predict(reshaped, verbose=1)

#---------------------------------ROLLING WINDOW MANIPULATIONS---------------------------------
def shift_window(arr, num, fill_value=np.nan):
    """builds a rolling window to store in short term memory
        input: array, index of window to shift
        output: shifted window, updated with new value at bottom"""
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

def reset_clock(array,index=3):
    """compensates time index of window for the fist few value of array
    input: window with first few values broken
    output: normalized window"""
    begin_value = array[index + 1][0]
    increment = begin_value / (index + 1)
    for i in range(index + 1):
        array[i][0] = i * increment
    return array

#------------------------------------SERIAL DECODING------------------------------------
def report(hex,time):
    """builds list of features from serial hex input"""
    power_factor, phase, P_real, P_reac, P_app, Vrms, Irms = decode(hex)
    # print('     Time', 'PF','Phase', 'P_real', 'P_reac', 'P_app,', 'V_rms', 'I_rms')
    val = [time, round(power_factor, 2), round(phase, 2), round(P_real, 2), round(P_reac, 2), round(P_app, 2),round(Vrms, 2), round(Irms, 2)]
    return val

def convert2bits(payload):
    """convert decimal string back to bitstream and to hex string """
    bits = ''.join([chr(int(b)) for b in payload.split()])
    hex = '0x' + binascii.hexlify(bits)
    return hex

def decode(a):
    """decode hex string to attributes"""
    # a = BitStream(hex)
    output = a.read("floatle:32"), a.read("floatle:32"), a.read("floatle:32"), a.read("floatle:32"), a.read("floatle:32"), a.read("floatle:32"), a.read("floatle:32")
    return output
