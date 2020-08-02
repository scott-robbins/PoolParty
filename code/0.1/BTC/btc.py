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

class Alarms:
    upper = 0
    lower = 0
    last_price = 0

    def __init__(self, parent):
        if not os.path.isfile('alarms.txt'):
            form = self.form = Tk.Toplevel(parent)
            self.set_top = Tk.Label(form, text='Upper Limit:').grid(row=0, column=0)
            self.set_low = Tk.Label(form, text='Lower Limit:').grid(row=1, column=0)
            self.top_val = Tk.Entry(form)
            self.low_val = Tk.Entry(form)
            self.top_val.grid(row=0, column=1)
            self.low_val.grid(row=1, column=1)
            enter = Tk.Button(form, text='Submit', command=self.write)
            enter.grid(row=3, column=1)
        else:
            print '[*] Alarms are already set'

    def write(self):
        self.upper = float(self.top_val.get())
        self.lower = float(self.low_val.get())
        self.form.destroy()
        dat = 'top:%f\nlow:%f\n' % (self.upper, self.lower)
        open('alarms.txt', 'w').write(dat)


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


def pull_btc_price_data():
    triggered = False
    # Send the setpoint to remote machine to check if current is above
    addr = '192.168.1.200'
    btc_file = '~/PoolParty/code/BTC/v0.1/btc_prices.txt'
    prices = list()
    deltas = list()
    moving_avg = list()
    stamps = list()
    if os.path.isfile('btc_prices.txt'):
        os.remove('btc_prices.txt')
    cmd = "nc -l 6666 >> btc_prices.txt & python utils.py cmd "+addr+ \
          " 'cat ~/PoolParty/code/BTC/v0.1/btc_prices.txt | nc -q 3 192.168.1.153 6666';clear"
    os.system(cmd)

    # Check for ALARMS
    if os.path.isfile('alarms.txt'):
        limits = utils.swap('alarms.txt', False)
        upper = limits[0].split(':')[1]
        lower = limits[1].split(':')[1]
        print upper
        print lower
        triggered = True
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

        msg = '    DATE: ' + stamps.pop().replace(']', '') + '     BTC PRICE: $' + str(price)
        levels = analysis.decision_tree_levels(prices, depth=5)
        prediction, y_lo, y_up, X, xx = analysis.quantitative_prediction(prices, depth=3,show=False)
        a.cla()
        a.grid()
        a.plot(np.array(prices), 'r', label='BTC Price [$]')
        a.plot(np.array(moving_avg), 'y', label='Moving Avg.')
        a.plot(levels, 'g', label='Decision Boundaries')
        xdom = range(np.array(prices).shape[0])
        if triggered:
            a.plot(xdom, float(upper)*np.ones(np.array(xdom).shape), 'w')
            a.plot(xdom, float(lower)*np.ones(np.array(xdom).shape), 'w')

        #                 NOW ADD BELLS!
        #
        #
        #     if price < lower:
        #         ohno = 'espeak -e "The Price is fucking low"'
        #         utils.ssh_command(addr,utils.names[addr],utils.retrieve_credentials(addr),ohno,False)
        #     if price < lower:
        #         ohno = 'espeak -e "The Price is fucking high"'
        #         utils.ssh_command(addr, utils.names[addr], utils.retrieve_credentials(addr), ohno, False)
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

        ''' Use Basic Red/Green/Blue Color system for indicating Market State '''
        if price > avged:  # Price is above Moving Average
            mkt_state = Tk.Label(root, text='MARKET STATE [+$]', bg='#00ff00')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#00ff00', bg='#000000')
            ticker.place(x=200, y=0, relwidth=0.36, relheight=0.1)
        elif price < avged:  # Price is below moving average
            mkt_state = Tk.Label(root, text='MARKET STATE [-$]', bg='#ff0000')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#ff0000', bg='#000000')
            ticker.place(x=200, y=0, relwidth=0.36, relheight=0.1)
        else:
            mkt_state = Tk.Label(root, text='MARKET STATE', bg='#0000ff')
            ticker = Tk.Label(root, textvariable=ticker_tape, height=20, fg='#0000ff', bg='#000000')
            ticker.place(x=200, y=0, relwidth=0.36, relheight=0.1)
        mkt_state.place(x=600, y=0, relwidth=0.15, relheight=0.1)
        tick.msg = msg[1:] + msg[0]
        ticker_tape.set(tick.msg)

        canvas.draw()
        canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
        canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)
        plt.show()
        root.after(1000 * 45, pull_btc_price_data)  # Continuously update every 45s


def tick(msg):
    tick.msg = msg[1:] + msg[0]
    ticker_tape.set(tick.msg)
    # root.after(scroll_speed, tick)


def add_alarms():
    Alarms(root)

# Add Buttons
button = Tk.Button(master=root, text='Quit', command=sys.exit)
button.place(x=0, y=0, relwidth=0.1, relheight=0.1)
canvas = FigureCanvasTkAgg(f, master=root)
# update = Tk.Button(master=root, text='Update', command=pull_btc_price_data)
# update.place(x=150, y=0, relwidth=0.1, relheight=0.1)
root.after(1000 * 35, pull_btc_price_data)  # Continuously update figure
pull_btc_price_data()

# canvas.draw()
# canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
# canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)

'''
Add A button for a sound alarm on certain price 
movement events!!

'''
bells = Tk.Button(master=root, text='Set Alarms', command=add_alarms)
bells.place(x=785,y=0,relwidth=0.1,relheight=0.1)
f.canvas.callbacks.connect('button_press_event', click_event)
Tk.mainloop()