import tensorflow as tf
import numpy as np
import utils
import time
import os


tic = time.time()
''' LOAD TRAINING DATA [HISTORIC BTC PRICES] '''
data_file = os.getcwd()+'/btc_prices.txt'
if os.path.isfile(data_file):
    raw_price_data = utils.swap(data_file, False)
else:
    print 'No Price data Found!'
    exit()
training_data = np.zeros((len(raw_price_data), 1))
data_pt = 0
for entry in raw_price_data:
    if len(entry.split('$'))>1:
        training_data[data_pt,0] = float(entry.split(' ')[0].split('$')[1])
        data_pt += 1
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0, 1))
training_set_scaled = sc.fit_transform(training_data)

# Divide Training Data into 60 Time Steps and 1 output
X_train = []
Y_train = []
for i in range(60,training_data.shape[0],int(np.floor(training_data.shape[0]/3440))):
    X_train.append(training_set_scaled[i-60:i,0])
    Y_train.append(training_set_scaled[i, 0])
X_train, Y_train = np.array(X_train), np.array(Y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

'''  BUILD RECURRENT NEURAL NETWORK  '''
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

# Initialize 1st LSTM Layers
regression = Sequential()
# Dropout regularization
regression.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1],1)))
regression.add(Dropout(0.2))
# Second LSTM Layer
regression.add(LSTM(units=50, return_sequences=True))
regression.add(Dropout(0.2))
# Third LSTM Layer
regression.add(LSTM(units=50, return_sequences=True))
regression.add(Dropout(0.2))
# Fourth LSTM Layer
regression.add(LSTM(units=50))
regression.add(Dropout(0.2))
# Final Fully Connected Layers
regression.add(Dense(units=1))
# Add Optimizer/Loss Function
regression.compile(optimizer='adam', loss='mean_squared_error')
# Fit RNN to Training Set
regression.fit(X_train, Y_train, epochs=10, batch_size=32)


# Load Test Data
raw_test_data = []
data_pt = 0
X_test = np.zeros((X_train.shape[0], 1))
for line in utils.swap('btc_test_data.txt', False):
    X_test[data_pt] = float(line.split('\t')[-1])
    data_pt += 1
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
print X_test.shape
recent = X_test[X_test.shape[0]-1:X_test.shape[0]-61, 0, 0]
print recent.shape
# Make A Prediction;
predicted_stock_price = regression.predict(recent)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

# print predicted_stock_price