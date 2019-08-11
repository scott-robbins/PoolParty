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
Width = 600
Height = 800


def on_click(event):
    date, timestamp  = utils.create_timestamp()
    if event.inaxes is not None:
        setpoint = event.ydata
        print 'SETPOINT \033[32m\033[1m$%s\033[0m' % str(setpoint)
        open('setpoint.txt','w').write(str(setpoint))
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
    setpoint = float(open('setpoint.txt', 'r').readlines().pop())

    ''' Calculate a Guess, 
        Write it to a file, 
        if file already exists:
         - log next guess, error of preview guess, etc.'''
    estimate = moving_avg.pop()+np.array(deltas).mean()
    print 'PRICE: $%s' % str(prices.pop())
    print 'GUESS = $%s' % str(estimate)
    a.cla()
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata, color='blue', linestyle='-.', label='Moving Average')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps[len(dates) - 1]))
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata, color='blue', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), color='green', label='Target Price')
    a.grid()
    canvas.draw()
    canvas.get_tk_widget().place(x=0,y=100,relwidth=1,relheight=0.8)
    canvas._tkcanvas.place(x=0,y=100,relwidth=1,relheight=0.8)
    plt.show()
    print 'GUESS = $%s' % str(estimate)


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
    button.place(x=0,y=0,relwidth=0.1,relheight=0.1)
    update = Tk.Button(master=root, text='Update', command=update_logs)
    update.place(x=150, y=0, relwidth=0.1, relheight=0.1)

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
    a.plot(pdata, color='red', linestyle=':', label='Price')
    a.plot(padata,color='blue', linestyle='-.',label='Moving Average')
    a.plot(setpoint*np.ones((len(pdata),1)), color='green', label='Target Price')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    canvas.draw()
    canvas.get_tk_widget().place(x=0,y=100,relwidth=1,relheight=0.8)
    canvas._tkcanvas.place(x=0,y=100,relwidth=1,relheight=0.8)

    f.canvas.callbacks.connect('button_press_event', on_click)
    basic_logic()

    if time.time()-tic > 1 and int(time.time()-tic) % 30 == 0:
        update_logs()

    Tk.mainloop()