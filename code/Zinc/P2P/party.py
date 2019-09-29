import Tkinter as Tk
import numpy as np
import engine
import utils
import time
import sys
import os

root = Tk.Tk()
colors = {'red': '#ff0000', 'green': '#00ff00', 'blue': '#0000ff'}
nodes = utils.prs


def execit():
    print 'Executing ...'


cx = np.linspace(0,1000,12)
ii = 0
for col in cx[0:3]:
    name = utils.names[nodes[ii]]
    pw = utils.retrieve_credentials(nodes[ii])
    utils.retrieve_credentials(nodes[ii])
    cmd = 'whoami'
    status = utils.ssh_command(nodes[ii], name, pw, cmd, True).replace('\n', '')
    if status == name:
        label = '[connected]'
        state = 'green'
    else:
        state = 'red'
        label = '[disconnected]'
    button = Tk.Button(master=root,text='CMD', bg=colors[state], command=execit)
    button.config(font=('Times', 10))
    button.place(x=10, y=col, relwidth=0.1, relheight=0.1)
    ii += 1

# Create console window


Tk.mainloop()
