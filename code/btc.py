import numpy as np
import urllib
import utils
import time
import sys
import os

btc_ticker = 'https://blockchain.info/ticker'
timeout = 20000000  # ~231 Days...
tic = time.time()
running = True


def update_ticker_data(log):
    data = ''
    stamp = utils.create_timestamp()
    for line in urllib.urlopen(btc_ticker).readlines():
        if "USD" in line:
            data = line.split(':')[2].split(',')[0].replace(' ', '')
    content = 'PRICE:\t' + data + '\tTIME:' + stamp[0] + '\t' + stamp[1] + '\n'
    if log:
        open('btc_price_ticker.txt','a').write(content)
    else:
        print '$%s\t[%s - %s]' % (str(data), stamp[1], stamp[0])
    return data, stamp


if 'run' in sys.argv:
    print '** Starting BTC Data Collection **'
    price_data = []
    mavg = []  # Moving Average
    dmavg = []  # Delta from Moving Average at each moment
    p0, t0 = update_ticker_data(False)
    if not os.path.isfile('btc_prices.txt'):
        open('btc_prices.txt', 'w').write('START %s\nCurrent\tavg\tdelta\tTime\n' % t0[0])

    while running and (time.time() - tic) <= timeout:
        print '\033[1m\033[32mBTC PRICE\t\033[31mTIME\033[0m'
        current_price, timestamp = update_ticker_data(False)
        price_data.append(np.float(current_price))
        avgp = np.array(price_data).mean()
        davg = float(current_price) - avgp
        mavg.append(avgp)
        dmavg.append(davg)
        if davg > 0.5:
            print '+$%s from Avg. $%s' % (str(davg), avgp)
        elif davg < 0.5:
            print '-$%s from Avg. $%s' % (str(davg), avgp)
        else:
            print 'Price is AT Avg. $%s' % str(avgp)
        line = '$%s\t$%s\t$%s\t[%s - %s]' % \
               (str(current_price), str(avgp), str(davg), timestamp[1], timestamp[0])
        open('btc_prices.txt', 'a').write(line + '\n')
        time.sleep(15)
        os.system('clear')
