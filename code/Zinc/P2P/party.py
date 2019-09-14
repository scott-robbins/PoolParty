import Tkinter as Tk
import engine
import utils
import time
import sys
import os

root = Tk.Tk()
colors = ['#ff0000', '#00ff00', '#0000ff']
rowy = 100
rowx = 0
i = 0
for ip in utils.prs:
    if ip in utils.names.keys():
        host = utils.names[ip]
        title = '%s [%s]' % (ip, host)
        node_label = Tk.Label(root, text=title, bg=colors.pop())
        node_label.place(x=rowx, y=rowy+i*rowy, relwidth=0.12, relheight=0.1)
        # node_label.place(x=rowx+i*rowx, y=rowy, relwidth=0.2, relheight=0.1)
        reply = utils.ssh_command(ip, host, utils.retrieve_credentials(ip), 'whoami', False)

        if host == reply.replace('\n', '').replace(' ', ''):
            online_label = Tk.Label(root, text=' ONLINE ', bg='#ffff00')
            online_label.place(x=rowx + 150, y=rowy + i * rowy, relwidth=0.1, relheight=0.1)
            print host
        i += 1

Tk.mainloop()
