from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from threading import Thread
import urllib
import base64
import socket
import utils
import time
import aes
import sys
import os

peers = ['192.168.1.200', '192.168.1.217', '192.168.1.229']
tic = time.time()


def socket_msgr(message, friend):
    timeout = 10
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((friend, 6666))
    s.send(message)
    tic = time.time()
    reply = ''
    try:
        while (time.time()-tic) <= timeout:
            reply = s.recv(1024)
    except KeyboardInterrupt:
        pass
    return reply


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


def encrypt(text, key):
    if key:
        c = AES.new(key)
    else:
        c = AES.new(base64.b64encode(get_random_bytes(16)))
    return aes.EncodeAES(c, text)


def listener(timeout):
    refresh = 20
    running = True
    tic = time.time()
    listen = Thread(target=utils.start_listener,args=('workers.txt', 6666, ))
    listen.start()
    listen.join()
    while time.time()-tic <= timeout and running:
        try:
            dt  = time.time()-tic
            if dt > 1 and int(dt) % refresh == 0:
                worker_data = utils.swap('workers.txt', True)
                # TODO: If length of worker data is nonzero, a message is
                #  waiting. Handle different messages accordingly.
                if len(worker_data) > 1:
                    for line in worker_data:
                        try:
                            msg = line.split('DATA READY ')[1]
                            print msg
                        except IndexError:
                            pass
        except KeyboardInterrupt:
            running = False
    kill_cmd = 'ps aux | grep "nc -l" | cut -b 10-15 | while read n; do kill -9 $n; done'
    os.system(kill_cmd)


if 'add' in sys.argv:
    if len(sys.argv) >= 3:
        add_host(sys.argv[2])
    else:
        print '\033[31m\033[1m\033[3mIncorrect Usage!\033[0m'
        exit()

