import matplotlib.pyplot as plt
import numpy as np
import urllib
import utils
import time
import sys
import os


btc_ticker = 'https://blockchain.info/ticker'
t0 = time.time()


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
        print '%$%s\t[%s - %s]' % (str(data), stamp[1], stamp[0])
    return data, stamp


