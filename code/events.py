from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
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
Width = 600
Height = 800


def on_click(event):
    if event.inaxes is not None:
        sp = event.ydata
        print 'SETPOINT \033[32m\033[1m$%s\033[0m' % str(sp)
        try:
            open('setpoint.txt', 'w').write(str(sp))
        except IOError:
            print '** Setpoint Unchanged **'
            pass
    else:
        'Clicked ouside bounds!'
    update_logs()


def update_logs():
    basic_logic()
    plt.close()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    os.system("rm btc_prices.txt; nc -l 6666 >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
              " cat ~/Desktop/PoolParty/code/btc_prices.txt | nc -q 2 192.168.1.153 6666'")

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
    setpoint = float(utils.swap('setpoint.txt', True).pop())

    ''' MODEL_1: Linear Regression '''
    x = np.array(range(len(prices)))
    lr = LinearRegression()
    lr.fit(x[:, np.newaxis], pdata)

    estimate = lr.predict(x[:, np.newaxis])[len(x)-1]
    error = price - estimate
    print 'PRICE: $%s' % str(prices.pop())
    print 'GUESS = $%s' % str(estimate)
    print '* Error: %s' % str(error)
    open('error.txt', 'a').write(str(error)+'\n')
    fit = lr.predict(x[:, np.newaxis]) + error

    '''     MODEL_2: Decision Tree Regressor    '''
    regr_1 = DecisionTreeRegressor(max_depth=4)
    X = x[:, np.newaxis]
    y = pdata
    regr_1.fit(X, y)
    y_1 = regr_1.predict(X)

    a.cla()
    a.set_ylabel('Price $ [USD]')
    a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps[len(dates) - 1]))
    a.plot(pdata, color='red', linestyle='--', label='Price')
    a.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':',color='orange', label='Target Price')
    a.plot(x, fit, 'b-',label='Linear Fit')
    a.plot(X, y_1, c="g", label="Decision Boundaries", linewidth=2)
    a.grid()
    a.legend()

    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)
    plt.show()


def basic_logic():

    setpoint = float(open('setpoint.txt', 'r').readlines().pop())
    if setpoint < prices.pop():
        print 'Setpoint is below current price'
    if setpoint > prices.pop():
        print 'Setpoint is above current price'
    if prices.pop() < moving_avg.pop():
        print '033[1mPrice is \033[31mBELOW \033m0m\033[1m Moving Average !!\033[0m'
    if prices.pop() == pdata.max():
        print '** 033[1mPrice is at an \033[32mAT ALL TIME HIGH \033m0m\033[1m Moving Average **\033[0m'


if 'run' in sys.argv:
    root = Tk.Tk()
    plt.style.use('dark_background')
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    button = Tk.Button(master=root, text='Quit', command=sys.exit)
    button.place(x=0, y=0, relwidth=0.1, relheight=0.1)
    update = Tk.Button(master=root, text='Update', command=update_logs)
    update.place(x=150, y=0, relwidth=0.1, relheight=0.1)

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(f, master=root)

    t0 = time.time()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    if not os.path.isfile('btc_prices.txt'):
        os.system("rm btc_prices.txt; nc -l 6666 >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
                  " cat ~/Desktop/PoolParty/code/btc_prices.txt | nc -q 2 192.168.1.153 6666'")
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
    setpoint = float(open('setpoint.txt', 'r').readlines().pop())

    if not os.path.isfile(os.getcwd()+'/btc_prices.txt'):
        print '\033[1mBTC Price Data Log \033[3mis NOT present!\033[0m'
        host = raw_input('Enter Name of Host \033[1mWith\033[0m btc_prices.txt: ')
        if host in utils.names:
            cmd = 'python client.py get %s %s' % (host, '/root/Desktop/PoolParty/code/btc_prices.txt')
            os.system(cmd)
    estimate = moving_avg.pop() + np.array(np.diff(pdata)).mean()
    print 'PRICE: $%s' % str(prices.pop())
    print 'GUESS = $%s' % str(estimate)
    a.grid()
    a.plot(pdata, color='red', linestyle='--', label='Price')
    a.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)

    f.canvas.callbacks.connect('button_press_event', on_click)
    basic_logic()

    if time.time()-tic > 1 and int(time.time()-tic) % 30 == 0:
        update_logs()

    Tk.mainloop()
