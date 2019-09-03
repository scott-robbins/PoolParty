from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import numpy as np
import utils
import time
import os


def get_price_data():
    tic = time.time()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    port = np.random.random_integers(4000, 65000, 1)[0]
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
    toc = time.time() - tic
    file_size = os.path.getsize('btc_prices.txt')/1000.
    print '\033[1m\033[32m%s Kb\033[0m BTC Price Data Pulled [%ss Elapsed]' % \
          (str(file_size), str(toc))
    return prices, moving_avg, deltas, stamps


''' Pull logs from a Pool Machine '''
price_data, avg, delta_data, dates = get_price_data()
price = np.array(price_data)
moving_avg = np.array(avg)
dprice = np.array(delta_data)
start = dates[0].replace(']','')
stop = dates.pop().replace(']','')
print 'Analyzing BTC Price Data from \033[3m\033[1m' + start+' to ' + stop + '\033[0m'

lr = LinearRegression()
ii = 0
N = 10

# A fit for every 1k points
dd = np.linspace(0,len(price), N)
for dx in np.linspace(0, len(price), N):
    if ii > 0 :
        xx = np.arange(dd[ii-1], dd[ii], 1)
        X = xx[:, np.newaxis]
        y = price[int(dd[ii-1]):int(dd[ii])]
        try:

            xx = np.arange(dd[ii - 1], dd[ii], 1)
            X = xx[:, np.newaxis]+dx
            if np.array(y).shape[0] != xx.shape[0]:
                y = price[int(dd[ii - 1]):int(dd[ii]) + 1]
            else:
                y = price[int(dd[ii -1]): int(dd[ii])]
            lr.fit(X, y)
        except ValueError:
            lr.fit(X, y)

        fit = lr.predict(X)
        # plt.plot(xx, fit,'--')
    ii += 1

# plt.grid()
# plt.plot(price,'g-')
# plt.show()