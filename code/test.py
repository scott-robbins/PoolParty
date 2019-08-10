from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import numpy as np
import urllib
import base64
import utils
import time
import aes
import sys
import os

peers = ['192.168.1.200', '192.168.1.217', '192.168.1.229']
btc_ticker = 'https://blockchain.info/ticker'
tic = time.time()


def create_timestamp():
    date = time.localtime(time.time())
    mo = str(date.tm_mon)
    day = str(date.tm_mday)
    yr = str(date.tm_year)

    hr = str(date.tm_hour)
    min = str(date.tm_min)
    sec = str(date.tm_sec)

    date = mo + '/' + day + '/' + yr
    timestamp = hr + ':' + min + ':' + sec
    return date, timestamp


def update_ticker_data(log):
    data = ''
    stamp = create_timestamp()
    for line in urllib.urlopen(btc_ticker).readlines():
        if "USD" in line:
            data = line.split(':')[2].split(',')[0].replace(' ', '')
    content = 'PRICE:\t' + data + '\tTIME:' + stamp[0] + '\t' + stamp[1] + '\n'
    if log:
        open('btc_price_ticker.txt', 'a').write(content)
    return data, stamp


def add_host(ip):
    uname = raw_input('Enter Username: ')
    pword = raw_input('Enter Password: ')
    datastr = '%s@%s:%s' % (uname, ip, pword)
    os.system('python aes.py -e '+datastr)
    file_out = ip.replace('.','')+'.txt'
    kname = ip.replace('.','')+'.key'
    if not os.path.isdir('Hosts'):
        os.mkdir('Hosts')
    os.system('cat encrypted.txt >> Hosts/%s; rm encrypted.txt' % file_out)
    os.system('cat key.txt >> Hosts/%s; rm key.txt' % kname)


if 'add' in sys.argv:
    if len(sys.argv) >= 3:
        add_host(sys.argv[2])
    else:
        print '\033[31m\033[1m\033[3mIncorrect Usage!\033[0m'
        exit()


def encrypt(text, key):
    if key:
        c = AES.new(key)
    else:
        c = AES.new(base64.b64encode(get_random_bytes(16)))
    return aes.EncodeAES(c, text)


if 'run_btc' in sys.argv:
    home = peers[0]
    refresh_rate = 2
    runnning = True
    price_data = []
    n_pts = 0
    while runnning:
        price, stamp = update_ticker_data(False)
        print '$%s [%s - %s]' % (str(price), stamp[1], stamp[0])
        price_data.append(price)
        n_pts = len(price_data)
        if n_pts > 1 and n_pts%refresh_rate == 0:
            print '\t\t~ PHONE HOME ~'
            # SEND PRICE DATA BACK TO MOTHERSHIP
            pword = utils.retrieve_credentials(home)
            utils.ftp_put(home,'root',pword,'btc_price_ticker.txt','~/Desktop/PoolParty/code/btcprices.txt')
