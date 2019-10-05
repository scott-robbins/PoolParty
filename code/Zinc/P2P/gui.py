import Tkinter as Tk
import numpy as np
import utils
import time
import sys
import os


def discover_nodes():
    active_nodes = {}
    for host in utils.prs:
        name = utils.names[host]
        pw = utils.retrieve_credentials(host)




tic = time.time()
root = Tk.Tk()

w = 1200
h = 800
cv = Tk.Canvas(root, height=h, width=w)
cv.pack()

# Add Quit Button
button = Tk.Button(master=cv, text='Quit', command=sys.exit)
button.place(x=0, y=0, relwidth=0.07, relheight=0.06)

# Add Title
title = Tk.Label(cv,text='P2P_CONTROL_DASHBOARD',bg='#00fff0')
title.place(x=w/2-150, h=0,relwidth=0.25, relheight=0.06)




Tk.mainloop()
