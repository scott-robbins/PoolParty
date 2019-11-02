from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import numpy as np
import utils
import time
import sys
import os

tic = time.time()


def get_btc_data():
    cmd = "nc -l 6666 >> btc_prices.txt & python utils.py cmd 192.168.1.200 " \
          "'cat ~/Desktop/PoolParty/code/BTC/v0.1/btc_prices.txt | nc -q 3 192.168.1.153 6666';"
    os.system(cmd)


def btc2csv(raw_prices, stamps, file_out):
    if len(raw_prices) != len(stamps):
        print '[!!] Dimension Mismatch %s:%s' % (str(raw_prices), str(len(stamps)))
        exit()
    content = ''
    N = len(stamps)
    for ii in range(N):
        content += '%s, %s' % (str(stamps[ii].split(' - ')[1]), str(raw_prices[ii])) + '\n'
    if os.path.isfile(file_out):
        # TODO:
        print '%s Already Exists. Are you sure you want to overwrite this file? (y/n)' % file_out
    open(file_out, 'w').write(content)


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


def quantitative_prediction(price_data, depth, show):
    a = 0.95
    clf = GradientBoostingRegressor(loss='quantile', alpha=a,
                                    n_estimators=250, max_depth=depth,
                                    learning_rate=.1, min_samples_leaf=9,
                                    min_samples_split=9)
    X = np.array(range(len(price_data)))[:, np.newaxis]
    xx = np.atleast_2d(range(len(price_data))).T
    xx = xx.astype(np.float32)
    clf.fit(X, price_data)
    y_up = clf.predict(xx)
    clf.set_params(alpha=1.0 - a)
    clf.fit(X, price_data)
    y_lo = clf.predict(xx)
    clf.set_params(loss='ls')
    clf.fit(X, price_data)
    # Make the prediction on the meshed x-axis
    pred = clf.predict(xx)
    print len(pred)
    if show:
        # plt.plot(xx, price_data,'g:', label='Price')
        plt.plot(X, price_data, 'r')
        plt.legend(loc='upper left')
        plt.fill(np.concatenate([xx, xx[::-1]]),
                 np.concatenate([y_up, y_lo[::-1]]),
                 alpha=.5, fc='b', ec='None', label='90% prediction interval')
        plt.show()
    return pred, y_lo, y_up, X, xx


if 'run' in sys.argv:
    if not os.path.isfile('btc_prices.txt'):
        get_btc_data()
    pdata, mavg, dprice, dates = parse_data()
    # plt.plot(np.array(pdata), 'b', label='btc price [$]')
    # plt.plot(np.array(mavg), 'r', label='moving avg.')

    if 'tree' in sys.argv:
        # Use Decision Tree Regression to Set Limits
        fit = decision_tree_levels(pdata)
        plt.plot(fit, 'g', label='Decision Tree')

    if '-q' in sys.argv:
        X = np.array(range(len(pdata)))[:, np.newaxis]
        xx = np.atleast_2d(np.linspace(0, 10, len(pdata))).T
        xx = xx.astype(np.float32)
        pred, y_lo, y_hi = quantitative_prediction(pdata, 3, True)
        plt.plot(X, pdata, 'r')
        plt.legend(loc='upper left')
        plt.fill(np.concatenate([xx, xx[::-1]]),
                 np.concatenate([y_hi, y_lo[::-1]]),
                 alpha=.5, fc='b', ec='None', label='90% prediction interval')
        plt.show()
    # plt.legend()
    # plt.grid()
    # plt.show()


