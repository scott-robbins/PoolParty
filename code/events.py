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
scroll_speed = 500


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


def tick():
    tick.msg = tick.msg[1:] + tick.msg[0]
    ticker_tape.set(tick.msg)
    root.after(scroll_speed, tick)


def update_logs():
    basic_logic()
    plt.close()
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

    pdata = np.array(prices)
    padata = np.array(moving_avg)
    setpoint = float(utils.swap('setpoint.txt', False).pop())

    a.cla()
    a.set_ylabel('Price $ [USD]')
    a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps.pop()))
    a.plot(pdata, color='red', linestyle='--', label='Price')
    a.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')

    ''' MODEL_1: Linear Regression 
    (should probably be refitted (or create new fit) after 1k points.
    '''
    if len(prices) > 10000:
        print 'Using %d LinearRegression Models in Series' % int(len(prices)/10000.)

        lr = LinearRegression()
        ii = 0
        N = 10

        ''' Generate fit iteratively for every 1k points '''
        dd = np.linspace(0, len(prices), N)
        for dx in np.linspace(0, len(prices), N):
            if ii > 0:
                xx = np.arange(dd[ii - 1], dd[ii], 1)
                X = xx[:, np.newaxis]
                y = prices[int(dd[ii - 1]):int(dd[ii])]
                try:

                    xx = np.arange(dd[ii - 1], dd[ii], 1)
                    X = xx[:, np.newaxis] + dx
                    if np.array(y).shape[0] != xx.shape[0]:
                        y = prices[int(dd[ii - 1]):int(dd[ii]) + 1]
                    else:
                        y = prices[int(dd[ii - 1]): int(dd[ii])]
                    lr.fit(X, y)
                except ValueError:
                    lr.fit(X, y)

                fit = lr.predict(X)
                a.plot(xx, fit, '--', c="y")
            ii += 1

    error = price - fit
    print '\033[1mPRICE: $%s' % str(prices.pop())
    print '\033[3m* Error: %s\033[0m' % str(error)
    # open('error.txt', 'a').write(str(error) + '\n')

    '''     MODEL_2: Decision Tree Regressor    '''
    x = np.array(range(len(prices)))
    regr_1 = DecisionTreeRegressor(max_depth=4)
    X = x[:, np.newaxis]
    y = prices
    regr_1.fit(X, y)
    y_1 = regr_1.predict(X)
    a.plot(X, y_1, c="g", label="Decision Boundaries", linewidth=3)
    a.grid()

    tick.msg = '    DATE: '+stamps.pop().replace(']', '')+'   BTC PRICE: $'+str(price)
    tick()
    ticker = Tk.Label(root, textvariable=ticker_tape, height=20)
    ticker.place(x=400, y=0, relwidth=0.1, relheight=0.1)

    if price > aprice: # Price is above Moving Average
        mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
    elif price < aprice: # Price is below moving average
        mkt_state = Tk.label(root, text='MARKET STATE [-$]', bg='#ff0000')
    else:
        mkt_state = Tk.label(root, text='MARKET STATE', bg='#0000ff')
    mkt_state.place(x=750,y=0,relwidth=0.1, relheight=0.1)

    date, ts = utils.create_timestamp()
    print ts

    if os.path.isfile('guess.txt'):
        error = float(open('guess.txt').readlines().pop())-price
        open('error.txt', 'a').write('%s - %s\tPredictionError: $%s' % (date,ts,str(error)))
    fit_slope = np.diff(np.array(fit)).mean()
    PREDICTION = fit_slope*20 +price
    GUESS = Tk.Label(root, text='5min. Prediction: $%s  [%s]' % (str(PREDICTION),ts), bg='#7c00a7', font=("Futura", 16),fg='white')
    GUESS.place(x=400, y=775, relwidth=0.5, relheight=0.12)  # SHOW WHAT Latest Linear Model Predicts
    open('guess.txt', 'w').write(str(price))

    if os.path.isfile('error.txt'):
        open('error.txt', 'a').write(str(error) + '\n')
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
        print '\033[1mPrice is \033[31mBELOW \033m0m\033[1m Moving Average !!\033[0m'
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
        port = np.random.random_integers(4000,65000,1)[0]
        os.system("rm btc_prices.txt; nc -l %d >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
                  " cat ~/Desktop/PoolParty/code/btc_prices.txt | nc -q 2 192.168.1.153 %d'" % (port,port))
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
            cmd = 'python client.py get %s %s -q' % (host, '/root/Desktop/PoolParty/code/btc_prices.txt')
            os.system(cmd)
    estimate = padata.mean() + np.array(np.diff(pdata)).mean()
    print '\033[1mPRICE: $%s\033[0m' % str(prices.pop())
    print '\033[1mGUESS = $%s\033[0m' % str(estimate)
    a.grid()
    a.plot(pdata, color='red', linestyle='--', label='Price')
    a.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    if price > aprice: # Price is above Moving Average
        mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
    elif price < aprice: # Price is below moving average
        mkt_state = Tk.label(root, text='MARKET STATE [-$]', bg='#ff0000')
    else:
        mkt_state = Tk.label(root, text='MARKET STATE', bg='#0000ff')
    mkt_state.place(x=750,y=0,relwidth=0.1, relheight=0.1)

    scroll_speed = 150
    ticker_tape = Tk.StringVar()
    tick.msg = '    DATE: ' + stamps.pop().replace(']', '') + '   BTC PRICE: $' + str(price)
    tick()
    ticker = Tk.Label(root, textvariable=ticker_tape, height=20)
    ticker.place(x=400, y=0, relwidth=0.1, relheight=0.1)

    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)

    f.canvas.callbacks.connect('button_press_event', on_click)
    basic_logic()

    if time.time()-tic > 1 and int(time.time()-tic) % 30 == 0:
        update_logs()
    os.system('python analysis.py -q')
    Tk.mainloop()
