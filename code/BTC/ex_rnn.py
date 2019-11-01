import matplotlib.pyplot as plt
import tensorflow as tf
from tqdm import tqdm
import pandas as pd
import numpy as np
import utils
import os

# cmd = "nc -l 6666 >> btc_price.txt & python utils.py cmd 192.168.1.200 " \
#       "'cat ~/Desktop/PoolParty/code/BTC/v0.1/btc_prices.txt | nc -q 3 192.168.1.153 6666';clear"
# os.system(cmd)


def load_test_data():
    prices = list()
    stamps = list()
    for line in utils.swap('btc_price.txt', False):
        try:
            price = float(line.split('$')[1].replace('\t', ' ').split(' ')[0])
            avged = float(line.split('$')[2].replace('\t', ' ').split(' ')[0])
            delta = float(line.split('$')[3].split('\t')[0])
            dates = line.split('\t[')[1].split(']')[0]
            stamps.append(dates)
            prices.append(price)
        except IndexError:
            pass
    return prices, stamps


def load_training_data():
    prices = list()
    stamps = list()
    for line in utils.swap('v0.1/btc_prices.txt', False):
        try:
            price = float(line.split('$')[1].replace('\t', ' ').split(' ')[0])
            dates = line.split('\t[')[1].split(']')[0]
            prices.append(price)
            stamps.append(dates)
        except IndexError:
            pass
    return prices, stamps


prices, stamps = load_test_data()
# Extra space for a prediction?
guess = list()
[prices.append(0) for x in range(420)]
series = np.array(prices)
print series.shape

n_windows = 20
n_input = 1
n_output = 1
r_neuron = 42
size_train = int(len(prices)*0.8)


train = series[0:size_train]
test = series[size_train:len(prices)-1]
print(train.shape, test.shape)

x_data = train[:size_train-1]
try:
    X_batches = x_data.reshape(-1, n_windows, n_input)
except ValueError:
    if x_data.shape[0]%n_windows!=0:
        m = x_data.shape[0] % n_windows
        dx = x_data.shape[0] - m
        x_data = train[0:dx]

        X_batches = x_data.reshape(-1, n_windows, n_input)


def create_batches(df, windows, input, output):
    # Create X
    x_data = train[:size_train-1] # Select the data
    # X_batch = x_data.reshape(-1, windows, input)  # Reshape the data
    try:
        X_batch = x_data.reshape(-1, n_windows, n_input)  #: create the right shape for the batch e.g (10, 20, 1)
    except ValueError:
        if x_data.shape[0] % n_windows != 0:
            m = x_data.shape[0] % n_windows
            dx = x_data.shape[0] - m
            x_data = train[0:dx]

            X_batch = x_data.reshape(-1, n_windows, n_input)  #: create the right shape for the batch e.g (10, 20, 1)

    # Create y
    y_data = train[n_output:size_train]
    # y_batch = y_data.reshape(-1, windows, output)

    try:
        y_batch = x_data.reshape(-1, n_windows, n_input)  #: create the right shape for the batch e.g (10, 20, 1)
    except ValueError:
        if y_data.shape[0] % n_windows != 0:
            m = y_data.shape[0] % n_windows
            dy = y_data.shape[0] - m
            y_data = train[0:dy]
            y_batch = y_data.reshape(-1, n_windows, n_input)
    return X_batch, y_batch


X_batches, y_batches = create_batches(df = train,
                                      windows = n_windows,
                                      input = n_input,
                                      output = n_output)
X_test, y_test = create_batches(df = test, windows = 20,input = 1, output = 1)
print(X_test.shape, y_test.shape)

X = tf.placeholder(tf.float32, [None, n_windows, n_input])
y = tf.placeholder(tf.float32, [None, n_windows, n_output])

basic_cell = tf.contrib.rnn.BasicRNNCell(num_units=r_neuron, activation=tf.nn.relu)
rnn_output, states = tf.nn.dynamic_rnn(basic_cell, X, dtype=tf.float32)

stacked_rnn_output = tf.reshape(rnn_output, [-1, r_neuron])
stacked_outputs = tf.layers.dense(stacked_rnn_output, n_output)
outputs = tf.reshape(stacked_outputs, [-1, n_windows, n_output])

learning_rate = 0.00314

loss = tf.reduce_sum(tf.square(outputs - y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
training_op = optimizer.minimize(loss)

init = tf.global_variables_initializer()
iteration = 3000

with tf.Session() as sess:
    init.run()
    bar = tqdm(total=iteration)
    for iters in range(iteration):
        sess.run(training_op, feed_dict={X: X_batches, y: y_batches})
        if iters % 150 == 0 and iters > 0:
            mse = loss.eval(feed_dict={X: X_batches, y: y_batches})
            # print(iters, "\tMSE:", mse)
            print '\t\033[1m[*] \033[32mIteration: %d MSE: %f\033[0m' % (iters, mse)
            bar.update(150)
    try:
        y_pred = sess.run(outputs, feed_dict={X: X_test})
    except ValueError:
        print 'Prediction Failed!'
        print ValueError.message

    bar.close()

    plt.title("Forecast vs Actual", fontsize=14)
    plt.plot(pd.Series(np.ravel(y_test)), "bo", markersize=8, label="Actual", color='green')
    plt.plot(pd.Series(np.ravel(y_pred)), "r.", markersize=8, label="Forecast", color='red')
    plt.legend(loc="lower left")
    plt.xlabel("Time")
    plt.show()