from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from threading import Thread
import Tkinter as Tk
import numpy as np
import urllib
import utils
import time
import sys
import os

btc_ticker = 'https://blockchain.info/ticker'

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


def update_logs():
    plt.close()
    os.system("python client.py get 192.168.1.200 '/root/Desktop/PoolParty/code/btc_prices.txt'")
    for line in utils.swap('btc_prices.txt', False):
         try:
             price = float(line.replace('\t', ' ').split('$')[1].replace(' ', ''))
             aprice = float(line.split('\t')[1].replace('$','').replace(' ', ''))
             delta = float(line.split('\t')[2].replace('$','').replace(' ', ''))
             dates = line.split('\t')[3].replace('$','').split(' - ')[1]
             stamps.append(dates)
             prices.append(price)
             moving_avg.append(aprice)
             deltas.append(delta)
         except IndexError:
             pass

    pdata = np.array(prices)
    padata = np.array(moving_avg)
    a.cla()
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata, color='blue', linestyle='-.', label='Moving Average')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps[len(dates) - 1]))
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata, color='blue', linestyle='-.', label='Moving Average')
    return a


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

if 'read' in sys.argv:
    root = Tk.Tk()
    plt.style.use('dark_background')
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    button = Tk.Button(master=root, text='Quit', command=sys.exit)
    button.pack(side=Tk.BOTTOM)
    timeout = 20000000
    running = True
    tic = time.time()
    update = Tk.Button(master=root, text='Update', command=update_logs)
    update.pack(side=Tk.BOTTOM)

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(f, master=root)


    t0 = time.time()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
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

    pdata = np.array(prices)
    padata = np.array(moving_avg)


    if not os.path.isfile(os.getcwd()+'/btc_prices.txt'):
        print '\033[1mBTC Price Data Log \033[3mis NOT present!\033[0m'
        host = raw_input('Enter Name of Host \033[1mWith\033[0m btc_prices.txt: ')
        if host in utils.names:
            cmd = 'python client.py get %s %s' % (host, '/root/Desktop/PoolParty/code/btc_prices.txt')
            os.system(cmd)


    a.grid()
    a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps[len(dates)-1]))
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata,color='blue', linestyle='-.',label='Moving Average')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    canvas.draw()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    Tk.mainloop()