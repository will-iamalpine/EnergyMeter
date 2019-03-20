# import standard libraries
import os
from sklearn import preprocessing
import helper_functions as hf
import tensorflow as tf
tf.enable_eager_execution()
import numpy as np

#-------------------------------------simple script to test your model is working------------------------------------

model_path = 'insert_your_path_here.h5'
model = tf.keras.models.load_model(model_path)

data_path = "insert_your_path_to_test_data_here"

def build_list(filepath,labels=[],data=[]):
    cwd = os.chdir(filepath)
    for appliance_type in os.listdir(cwd):
        if appliance_type.endswith('.csv'):
            label = appliance_type.split("_")[0] #label is in title, before "_"
            labels.append(label)
            app_arr = np.genfromtxt(appliance_type, delimiter=',')
            data.append(np.array(app_arr))
    return labels,data

labels,data = build_list(data_path)
data = np.array(data)
print(labels)
print(data.shape)

#N.B. update this with each model!
appliance_dict = {0: 'cell', 1: 'desklamp', 2: 'fan', 3: 'kettle', 4: 'laptop', 5: 'monitor', 6: 'none', 7: 'sadlamp'}

for index,window in enumerate(data):
	print("-------------------")
	print('actual:',labels[index])
	# print(window.shape)
	prediction = hf.classify_device(window,model)  # classifies current device
	# print('prediction:', prediction, type(prediction), prediction.shape)
	device = tf.argmax(prediction, axis=-1).numpy()
	print('guess:', device,appliance_dict.get(device[0]))
	for j in range(0, len(appliance_dict)):  # for j in range (10):
		print(('guesses: %.2f%% %s' % (100 * prediction[0, j], appliance_dict.get(j))))


