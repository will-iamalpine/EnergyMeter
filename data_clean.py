import os
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import tensorflow as tf

def process_data(filepath,labels=[],data=[]):
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))  # define range for scale operation
    vars = ['time', 'power_factor', 'phase_angle', 'power_real', 'power_reactive', 'power_apparent', 'vrms', 'irms']
    os.chdir(filepath)
    for appliance_type in os.listdir("."):
        #print("\n",appliance_type)
        if appliance_type.endswith('.csv'):
            #split_file = str(filename).split("_")
            #print(appliance_type)
            app_df = pd.read_csv(filepath + appliance_type)
            app_df.columns = app_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
            app_arr = []
            # data_row = []
            for i in range(0, len(app_df['time'])):
                data_row = []
                for column in vars:
                    data_row.append(app_df[column][i])
                app_arr.append(data_row)
            app_arr_normalized = min_max_scaler.fit_transform(app_arr) #must scale when in 2D array form
            # print('app_arr:',app_arr,"\nX_train_minmax\n:",X_train_minmax)

            # data.append(app_arr)
            data.append(app_arr_normalized)
            print(app_df['app_desc'][0], app_df['app_name'][0])
            if app_df['app_desc'][0] == 'cell':
                labels.append('cell')
            else:
                labels.append(str(app_df['app_name'][0]).split('-')[0])
    return labels,data







