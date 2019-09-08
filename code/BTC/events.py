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
scroll_speed = 200


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


def pull_price_data():
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    port = np.random.random_integers(4000, 65000, 1)[0]  # Randomized Port Helps prevent socket creation errs
    os.system("rm btc_prices.txt; nc -l %d >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
              " cat ~/Desktop/PoolParty/code/BTC/btc_prices.txt | nc -q 2 192.168.1.153 %d'" % (port, port))

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
    return prices, moving_avg, deltas, stamps


def update_logs():
    basic_logic()
    plt.close()
    prices, moving_avg, deltas, stamps = pull_price_data()
    setpoint = float(utils.swap('setpoint.txt', False).pop())
    os.system('clear')

    try:
        a.cla()
        a.set_ylabel('Price $ [USD]')
        a.set_title('BTC Price Data [%s - %s]' % (stamps[0], stamps.pop()))
    except:
        print '\033[31m\033[3m ** Plotting Error!! **\033[3m'
    a.plot(prices, color='red', linestyle='--', label='Price')
    a.plot(moving_avg, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')

    if len(pdata) > 10000:
        ''' MODEL_1: Linear Regression (create new fit every 10k points) '''
        print 'Using %d LinearRegression Models in Series' % int(len(pdata)/10000.)

        lr = LinearRegression()
        ii = 0
        N = 12
        dff = []
        dfi = []
        ''' Generate fit iteratively for every 10k points '''
        dd = np.linspace(0, len(pdata), N)
        for dx in np.linspace(0, len(pdata), N):
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
                # TODO: Keep track of the discontinuities between
                fit = lr.predict(X)
                fi = fit.flatten()[0]
                ff = fit.flatten()[-1]
                dff.append(ff)
                dfi.append(fi)
                print 'Fit Start: $%s\tFit End: $%s' % (str(fi), str(ff))
                a.plot(xx, fit, '--', c="y")
            ii += 1
        print 'dFitStart:%s\tdFitEnd:%s' % (str(np.array(dfi).mean()), str(np.array(dff).mean()))
    # TODO: log price passing through points of support/resistance and adjust them accordingly
    resistance_0 = np.array(dfi).mean()
    resistance_1 = np.array(dff).mean()
    price = prices.pop()
    error = price - fit
    guess = np.diff(np.array(prices[len(prices)-121:len(prices)]))+price
    domain = np.array(range(len(prices),len(prices)+120))[:, np.newaxis]
    lr.fit(domain, guess)
    domain = np.array(range(len(prices)-500, len(prices) + 1000))[:, np.newaxis]
    a.plot(domain, lr.predict(domain), '-', c="white",label='Prediction')

    print '\033[1mPRICE: $%s' % str(price)
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
    a.legend()

    tick.msg = '    DATE: '+stamps.pop().replace(']', '')+'     BTC PRICE: $'+str(price)
    tick()

    ''' Use Basic Red/Green/Blue Color system for indicating Market State '''
    if price > aprice: # Price is above Moving Average
        mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
        ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#00ff00',bg='#000000')
        ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)
    elif price < aprice: # Price is below moving average
        mkt_state = Tk.Label(root, text='MARKET STATE [-$]', bg='#ff0000')
        ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#ff0000',bg='#000000')
        ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)
    else:
        mkt_state = Tk.Label(root, text='MARKET STATE', bg='#0000ff')
        ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#0000ff',bg='#000000')
        ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)
    mkt_state.place(x=550,y=0,relwidth=0.15, relheight=0.1)

    date, ts = utils.create_timestamp()
    print ts

    ''' Log Predictions and their errors over time (use for creating better models?) '''
    if os.path.isfile('guess.txt'):
        error = float(open('guess.txt').readlines().pop())-price
        open('error.txt', 'a').write('%s - %s\tPredictionError: $%s\n' % (date,ts,str(error)))
    fit_slope = np.diff(np.array(fit)).mean()
    PREDICTION = fit_slope*20 + price
    GUESS = Tk.Label(root, text='5min. Prediction: $%s (%s)[%s]' %
                                (str(PREDICTION), str(PREDICTION-price), ts),
                                 bg='#7c00a7', font=("Futura", 16), fg='white')
    GUESS.place(x=100, y=775, relwidth=0.9, relheight=0.12)  # SHOW WHAT Latest Linear Model Predicts
    open('guess.txt', 'w').write(str(price))

    ''' Update the Tk Figure Window '''
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)
    plt.show()  # TODO: Automatically update the display every 30 seconds?


def resize_window():
    print 'RESIZE'


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
    try:
        os.remove('btc_prices.txt')
    except IOError:
        pass

    root = Tk.Tk()
    plt.style.use('dark_background')
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    button = Tk.Button(master=root, text='Quit', command=sys.exit)
    button.place(x=0, y=0, relwidth=0.1, relheight=0.1)
    update = Tk.Button(master=root, text='Update', command=update_logs)
    update.place(x=150, y=0, relwidth=0.1, relheight=0.1)
    canvas = FigureCanvasTkAgg(f, master=root)

    t0 = time.time()
    prices = []
    moving_avg = []
    deltas = []
    stamps = []
    if not os.path.isfile('btc_prices.txt'):
        port = np.random.random_integers(4000,65000,1)[0]
        os.system("rm btc_prices.txt; nc -l %d >> btc_prices.txt & python client.py cmd 192.168.1.200 'sleep 1;"
                  " cat ~/Desktop/PoolParty/code/BTC/btc_prices.txt | nc -q 2 192.168.1.153 %d'" % (port,port))

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
    try:
        estimate = padata.mean() + np.array(np.diff(pdata)).mean()
        print '\033[1mPRICE: $%s\033[0m' % str(pdata.flatten()[-1])
        print '\033[1mGUESS = $%s\033[0m' % str(estimate)
    except:
        print 'btc_prices.txt file is broken !?... '

    ''' PLOT BTC PRICE DATA '''
    a.grid()
    a.plot(pdata, color='red', linestyle='--', label='Price')
    a.plot(padata, color='cyan', linestyle='-.', label='Moving Average')
    a.plot(setpoint * np.ones((len(pdata), 1)), linestyle=':', color='orange', label='Target Price')
    a.legend()
    a.set_ylabel('Price $ [USD]')
    plt.show()

    if price > aprice:  # Price is above Moving Average
        mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
    elif price < aprice:  # Price is below moving average
        mkt_state = Tk.Label(root, text='MARKET STATE [-$]', bg='#ff0000')
    else:
        mkt_state = Tk.Label(root, text='MARKET STATE', bg='#0000ff')
    mkt_state.place(x=550,y=0,relwidth=0.15, relheight=0.1)

    ticker_tape = Tk.StringVar()
    tick.msg = '    DATE: ' + stamps.pop().replace(']', '') + '   BTC PRICE: $' + str(price)
    tick()
    ticker = Tk.Label(root, textvariable=ticker_tape, height=20)
    ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)

    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)

    f.canvas.callbacks.connect('button_press_event', on_click)
    basic_logic()

    if time.time()-tic > 1 and int(time.time()-tic) % 30 == 0:
        update_logs()
    os.system('python analysis.py -q')

    '''
    TODO: This has gotten really messy, inflexible and unstable. 
    It's only like 250 lines, might be worth taking the best functioning
    elements of this script and starting clean (and keeping it clean, hopefully). 
    '''
    Tk.mainloop()
