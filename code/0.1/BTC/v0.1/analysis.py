from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import numpy as np
import utils
import time
import sys
import os


def analyze(show):
    t0 = time.time()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    port = np.random.random_integers(4000,65000,1)[0]
    os.system("rm btc_prices.txt; nc -l %d >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
              " cat ~/Desktop/PoolParty/code/btc_prices.txt | nc -q 2 192.168.1.153 %d'" % (port, port))
    for line in utils.swap('btc_prices.txt', False):
        try:
            price = float(line.replace('\t', ' ').split('$')[1].replace(' ', ''))
            aprice = float(line.split('\t')[1].replace('$', '').replace(' ', ''))
            delta = float(line.split('\t')[2].replace('$', '').replace(' ', ''))
            dates = line.split('\t')[3].replace('$', '').split(' - ')[1]
            stamps.append(dates)
            prices.append(price)
            moving_avg.append(aprice)
            deltas.append(delta)
        except IndexError:
            pass
    if price:
    	print '\033[1mCurrent Price: \033[32m$%s\033[0m' % price
    pdata = np.array(prices)
    padata = np.array(moving_avg)
    setpoint = float(open('setpoint.txt', 'r').readlines().pop())

    dtr = DecisionTreeRegressor(max_depth=4)
    lr = LinearRegression()
    x = np.array(range(len(prices)))
    X = x[:, np.newaxis]
    y = pdata

    # TODO: Need a fit for every 1k points
    lr.fit(X, pdata)
    dtr.fit(X, y)
    y0 = lr.predict(X)
    y1 = dtr.predict(X)
    last = pdata[len(pdata)-1]
    # Now Determine Error(s), and where
    err_y0 = y0[len(y0)-1] - last  # Correct Linear Model
    diff_y1 = y1[len(y1)-1] - last    # Make a guess based on decision tree, linear model and history models

    slope = (float(y0[len(y0)-1])-float(y0[0]))/len(y0)
    offset = pdata[0]
    pred_5min = slope*len(pdata)+(y0[len(y0)-1]+padata[len(padata)-1])/2+diff_y1
    err_pred = pred_5min - last
    print 'Error in Linear Model: %s' % str(err_y0)
    print 'Error in DTRegression Model: %s' % str(diff_y1)
    print '%fx + %s =Predicting=> ~$%s' % (slope, offset, str(pred_5min)) # TODO: LOG PREDICTIONS!
    date, timestamp = utils.create_timestamp()
    data = '%fx + %s+..~..=%s\t %d Points (+/- %s)\t[%s - %s]\n' % (slope, offset,str(pred_5min), len(pdata), err_pred, date, timestamp)
    if os.path.isfile('fit_history.txt'):
        open('fit_history.txt', 'a').write(data)
    else:
        open('fit_history.txt', 'w').write(data)

    print '[*] Analysis Complete (%ss Elapsed)' % str(time.time()-t0)
    if show:
        plt.style.use('dark_background')
        plt.plot(pdata, color='red', linestyle='--', label='Price')
        plt.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
        plt.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')
        plt.plot(X, y0, 'b-', label='Linear Fit')
        plt.plot(X, y1, c="g", label="Decision Boundaries", linewidth=2)
        plt.grid()
        plt.show()


verbose = True
if '-q' in sys.argv:
    analyze(False)
else:
    analyze(verbose)
