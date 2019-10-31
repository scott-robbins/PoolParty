from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter as Tk
import numpy as np
import analysis
import utils
import time
import sys
import os


''' INITIALIZE'''
plt.style.use('dark_background')
root = Tk.Tk()
f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)
ticker_tape = Tk.StringVar()
ticker = Tk.Label(root, textvariable=ticker_tape, height=20)
scroll_speed = 400
tic = time.time()


def click_event(event):
    if event.inaxes is not None:
        sp = event.ydata
        print 'SETPOINT \033[32m\033[1m$%s\033[0m' % str(sp)
        try:
            open('setpoint.txt', 'w').write(str(sp))
        except IOError:
            print '** Setpoint Unchanged **'
            pass
        pull_btc_price_data()


def tick():
    tick.msg = tick.msg[1:] + tick.msg[0]
    ticker_tape.set(tick.msg)
    root.after(scroll_speed, tick)


def pull_btc_price_data():

    prices = list()
    deltas = list()
    moving_avg = list()
    stamps = list()
    if os.path.isfile('btc_prices.txt'):
        os.remove('btc_prices.txt')
    cmd = "nc -l 6666 >> btc_prices.txt & python utils.py cmd 192.168.1.200 " \
          "'cat ~/Desktop/PoolParty/code/BTC/v0.1/btc_prices.txt | nc -q 3 192.168.1.153 6666';clear"
    os.system(cmd)
    if len(utils.swap('btc_prices.txt', False))> 1:
        for line in utils.swap('btc_prices.txt', False):
            try:
                price = float(line.split('$')[1].split(' ')[0].replace(' ', ''))
                avged = float(line.split('$')[2].split(' ')[0].replace(' ', ''))
                delta = float(line.split('$')[3].split('\t')[0])
                dates = line.split('\t[')[1].split(']')[0]
                stamps.append(dates)
                prices.append(price)
                deltas.append(delta)
                moving_avg.append(avged)
            except IndexError:
                pass
        tick.msg = '    DATE: ' + stamps.pop().replace(']', '') + '     BTC PRICE: $' + str(price)
        levels = analysis.decision_tree_levels(prices, depth=5)
        prediction, y_lo, y_up, X, xx = analysis.quantitative_prediction(prices, depth=3,show=False)
        a.cla()
        a.grid()
        a.plot(np.array(prices), 'r', label='BTC Price [$]')
        a.plot(np.array(moving_avg), 'y', label='Moving Avg.')
        a.plot(levels, 'g', label='Decision Boundaries')
        # ################ Highlight 90% Confidence Region(s) ################ #
        a.fill(np.concatenate([xx, xx[::-1]]),
                 np.concatenate([y_up, y_lo[::-1]]),
                 alpha=.5, fc='b', ec='None', label='90% prediction interval')
        # ##################################################################### #
        a.legend()
        print '%d Lines of Live BTC Price Data Accumulated' % len(utils.swap('btc_prices.txt', False))
        print '%d Prices Logged' % len(prices)
        if os.path.isfile('setpoint.txt'):
            setpoint = float(utils.swap('setpoint.txt', False).pop().replace('\n', '').replace(' ', ''))
            a.plot(np.ones((len(prices),1))*setpoint)

    try:
        ''' Use Basic Red/Green/Blue Color system for indicating Market State '''
        if price > avged:  # Price is above Moving Average
            mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#00ff00', bg='#000000')
            ticker.place(x=200, y=0, relwidth=0.2, relheight=0.1)
        elif price < avged:  # Price is below moving average
            mkt_state = Tk.Label(root, text='MARKET STATE [-$]', bg='#ff0000')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#ff0000', bg='#000000')
            ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)
        else:
            mkt_state = Tk.Label(root, text='MARKET STATE', bg='#0000ff')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#0000ff', bg='#000000')
            ticker.place(x=300, y=0, relwidth=0.2, relheight=0.1)
        mkt_state.place(x=600, y=0, relwidth=0.15, relheight=0.1)
    except UnboundLocalError:
        pass

    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
    canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)
    plt.show()

    tick()
    root.after(1000 * 60, pull_btc_price_data)  # Continuously update figure


# Add Buttons
button = Tk.Button(master=root, text='Quit', command=sys.exit)
button.place(x=0, y=0, relwidth=0.1, relheight=0.1)
canvas = FigureCanvasTkAgg(f, master=root)
# update = Tk.Button(master=root, text='Update', command=pull_btc_price_data)
# update.place(x=150, y=0, relwidth=0.1, relheight=0.1)


pull_btc_price_data()
canvas.draw()
canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)
f.canvas.callbacks.connect('button_press_event', click_event)
root.after(1000 * 30, pull_btc_price_data)  # Continuously update figure

Tk.mainloop()