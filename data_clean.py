import os
import glob
import numpy as np
import pandas as pd

data_path = '/Users/willbuchanan/Google Drive/ricky-will-louis/data/training/'
var_names = {'power_factor': 'Power factor', 'phase_angle': 'Phase angle', 'power_real': 'Real power',
 'power_reactive': 'Reactive power', 'power_apparent': 'Apparent power', 'vrms': 'RMS voltage', 'irms': 'RMS current'}

os.chdir('/Users/willbuchanan/Google Drive/ricky-will-louis/data/training/')

vars = ['time','power_factor','phase_angle','power_real', 'power_reactive', 'power_apparent', 'vrms', 'irms']

data_path = '/Users/willbuchanan/Google Drive/ricky-will-louis/data/training/'
os.chdir(data_path)

train_labels = []
train_data = []
for appliance_type in os.listdir("."):
    if appliance_type.endswith('.csv'):
        #split_file = str(filename).split("_")
        print(appliance_type)
        app_df = pd.read_csv(data_path + appliance_type)
        app_df.columns = app_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
        app_arr = []
        data_row = []
        for i in range(0, len(app_df['time'])):
            data_row = []
            for column in vars:
                data_row.append(app_df[column][i])
            app_arr.append(data_row)
        #app_np = np.asarray(app_arr)
        data_train.append(app_arr)
        train_labels.append(str(app_df['app_name'][0]).split('-')[0])

data_train_np = np.array(data_train)
