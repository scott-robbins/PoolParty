from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter as Tk
import numpy as np
import utils
import time
import sys
import os

tic = time.time()
btc_ticker = 'https://blockchain.info/ticker'


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
    root = Tk.Tk()
    plt.style.use('dark_background')
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    button = Tk.Button(master=root, text='Quit', command=sys.exit)
    button.pack(side=Tk.BOTTOM)
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
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata,color='blue', linestyle='-.',label='Moving Average')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    canvas.draw()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    Tk.mainloop()