from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import numpy as np
import utils
import time
import sys
import os


def get_btc_data():
    cmd = "nc -l 6666 >> btc_prices.txt & python utils.py cmd 192.168.1.200 " \
          "'cat ~/Desktop/PoolParty/code/BTC/v0.1/btc_prices.txt | nc -q 3 192.168.1.153 6666';"
    os.system(cmd)


def parse_data():
    prices = list()
    deltas = list()
    moving_avg = list()
    stamps = list()
    for line in utils.swap('btc_prices.txt', False):
        try:
            price = float(line.split('$')[1].split(' ')[0].replace(' ', ''))
            avged = float(line.split('$')[2].split(' ')[0].replace(' ', ''))
            delta = float(line.split('$')[3].split('\t')[0])
            dates = line.split('\t[')[1].split(']')[0]
            stamps.append(dates)
            prices.append(price)
            deltas.append(delta)
            moving_avg.append(avged)
        except IndexError:
            pass
    return prices, moving_avg, deltas, stamps


def decision_tree_levels(p, depth):
    xdom = np.array(range(len(p)))[:, np.newaxis]
    # Fit regression model 1
    regr_1 = DecisionTreeRegressor(max_depth=depth)
    # Fit regression model 2
    regr_1.fit(xdom, np.array(p)[:, np.newaxis])
    # Predict
    y_1 = regr_1.predict(xdom)
    return y_1


if 'run' in sys.argv:
    if not os.path.isfile('btc_prices.txt'):
        get_btc_data()
    pdata, mavg, dprice, dates = parse_data()
    plt.plot(np.array(pdata), 'b', label='btc price [$]')
    plt.plot(np.array(mavg), 'r', label='moving avg.')

    if 'tree' in sys.argv:
        # Use Decision Tree Regression to Set Limits
        fit = decision_tree_levels(pdata)
        plt.plot(fit, 'g', label='Decision Tree')

    plt.legend()
    plt.grid()
    plt.show()


