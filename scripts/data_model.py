import os
import warnings                                  # `do not disturbe` mode
warnings.filterwarnings('ignore')

import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations
import matplotlib.pyplot as plt                  # plots
import seaborn as sns                            # more plots
import pickle

sudo TMPDIR=/data/vincents/ pip install --cache-dir=/data/vincents/ --build /data/vincents/ matplotlib
from sklearn.metrics import mean_squared_log_error
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import tensorflow as tf
from sklearn.metrics import confusion_matrix, accuracy_score,roc_curve, auc,roc_auc_score,classification_report
from sklearn.svm import SVC

data_path = "/Users/louis/Google Drive/ricky-will-louis/data/training/"


def convert_str_to_int(str_list,keys): #converts labels from string to integer
  list_int = []
  for i in str_list:
    list_int.append(appliance_dict[i])
  return list_int

def convert_int_to_str(integer,keys):
  for appliance,index in keys.items():
    if index == integer:
        #print(integer,appliance)
        return appliance

def make3D(array,n): #adds channels to array to simulate an image
  return (np.stack((array,)*n, axis=-1))

labels=[]
def process_data(filepath,labels=[],data=[]):
    vars = ['time', 'power_factor', 'phase_angle', 'power_real', 'power_reactive', 'power_apparent', 'vrms', 'irms']
    cwd = os.chdir(filepath)
    for appliance_type in os.listdir(cwd):
       #print(“\n”,appliance_type)
       if appliance_type.endswith('.csv'):
            app_df = pd.read_csv(filepath + appliance_type)
            app_df.columns = app_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
            app_arr = []
            for i in range(0, len(app_df['time'])):
               data_row = []
               for column in vars:
                   data_row.append(app_df[column][i])
               if i <=45: #truncates at 50 rows
                 app_arr.append(data_row)

            data.append(np.array(app_arr))
            label = str(app_df['app_name'][0]).split('-')[0]
            labels.append(label)
    return labels,data

dataset_labels_str,dataset_data = process_data(data_path) #extracts CSV into labels & data
# dataset_data_np = tf.keras.preprocessing.sequence.pad_sequences(np.asarray(dataset_data), value=0, maxlen=50) #pads length to 50
dataset_data_np = np.asarray(dataset_data)

print(set(dataset_labels_str))


#--------------------extracts labels & assigns to appliance dictionary--------------------


labelset = list(set(dataset_labels_str))

appliance_dict = {}
for i,appliance in enumerate(labelset):
  appliance_dict[appliance] = i
print('appliance_dict',appliance_dict)

dataset_labels_int = convert_str_to_int(dataset_labels_str, appliance_dict) #converts from strings to integer
print('label sample:',dataset_labels_int[:5],dataset_labels_str[:5])

min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))  # define range for scale operation
scaled_dataset = []
for i,sample in enumerate(dataset_data_np):
    app_arr_normalized = min_max_scaler.fit_transform(sample) #must scale when in 2D array form
    scaled_dataset.append(app_arr_normalized)

scaled_dataset = np.array(scaled_dataset)
scaled_dataset_3D = make3D(scaled_dataset,3)

# -- Split data into training and test subsets
data_train, data_test, labels_train, labels_test = train_test_split(scaled_dataset, dataset_labels_str, test_size=0.20)#, random_state=42) #initialize random_state to get same result every time
print('train data shape:',data_train.shape,'# of train labels:',len(labels_train),'\nunique train labels:',set(labels_train))
print('test data shape:',data_test.shape,'# of test labels:',len(labels_test),'\nunique test labels:',set(labels_test))

for i,data in enumerate(scaled_dataset):
    if (data.shape != (50,8)):
        print(data.shape)
        print('index', i)


# num_labels = len(set(labels_train))
# print(num_labels,'labels created')

# # Let's first make sure the shape and type of our data is correct.
# # Convert data to float32 datatype and labels to int64 datatype.
# train_data = tf.cast(data_train, tf.float32)
# train_labels = tf.cast(labels_train, tf.int64)
# test_data = tf.cast(data_test, tf.float32)
# test_labels = tf.cast(labels_test, tf.int64)

# # When working with images, TensorFlow needs them to be shape [H, W, C], but
# # # our data is just [H, W] right now since its black and white. Let's add a extra channel axis.
# train_data = train_data[..., tf.newaxis]
# test_data = test_data[..., tf.newaxis]

# # # Now were ready to create Tensorflow Datasets!
# train_dataset = tf.data.Dataset.from_tensor_slices((train_data, train_labels))
# test_dataset = tf.data.Dataset.from_tensor_slices((test_data, test_labels))


# # Finally, let's shuffle our training data and batch it so its more efficient.
# train_dataset = train_dataset.shuffle(20).batch(1000)
# test_dataset = test_dataset.shuffle(20).batch(1000)


# -- Transform data labels from string to int for use in model
le = preprocessing.LabelEncoder()
le.fit(list(set(dataset_labels_str)))
train_labels = le.transform(labels_train)
test_labels = le.transform(labels_test)

label_list = le.classes_

# # -- Reshape train data for use in model
nsamples, nx, ny = data_train.shape
train_data_2d = data_train.reshape((nsamples,nx*ny))

# # -- Reshape test data for use in model
nsamples, nx, ny  = data_test.shape
test_data_2d = data_test.reshape((nsamples,nx*ny))

nsamples, nx, ny  = scaled_dataset.shape
dataset_data_np_2d = scaled_dataset.reshape((nsamples,nx*ny))


import pickle
filename = '/Users/louis/Google Drive/ricky-will-louis/models/lq_rf_model_1.sav'
rf = RandomForestClassifier(n_estimators=250, max_depth=4, random_state=0)

rf.fit(train_data_2d, labels_train)
rf_pred = rf.predict(test_data_2d)

pickle.dump(rf, open(filename, 'wb'), protocol=2)

sns.set(font_scale=1.2)
conf_mat = confusion_matrix(labels_test, rf_pred)
fig, ax = plt.subplots(figsize=(12,10))
sns.heatmap(conf_mat, annot=True, fmt='d',
            xticklabels=label_list, yticklabels=label_list)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()


filename = '/Users/louis/Google Drive/ricky-will-louis/models/lq_svc_model_1.sav'
svc = SVC(C=10, gamma=0.01, decision_function_shape='ovo')

svc.fit(train_data_2d, labels_train)
svc_pred = svc.predict(test_data_2d)

pickle.dump(svc, open(filename, 'wb'), protocol=2)

sns.set(font_scale=1.2)
conf_mat = confusion_matrix(labels_test, svc_pred)
fig, ax = plt.subplots(figsize=(12,10))
sns.heatmap(conf_mat, annot=True, fmt='d',
            xticklabels=label_list, yticklabels=label_list)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()


loaded_model = pickle.load(open(filename, 'rb'))

svc_pred = loaded_model.predict(test_data_2d)

print("Test Accuracy: %.3f%%" % (accuracy_score(test_labels, rf)*100))
print(classification_report(test_labels, rf, target_names=label_list))

for i,data in enumerate(test_data_2d):
  # print('data.shape',data.shape)
  data_re = data.reshape(1,-1)
  # print('data.reshape',data_re.shape)
  guess = loaded_model.predict(data_re)
  # print(guess)
  print('actual:',test_labels[i], label_list[test_labels[i]])
  print('predicted:', guess)

  guess_list.argmax

