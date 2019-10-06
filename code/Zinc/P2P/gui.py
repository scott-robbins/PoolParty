import Tkinter, Tkconstants, tkFileDialog
import Tkinter as Tk
import numpy as np
import utils
import time
import sys
import os

tic = time.time()
root = Tk.Tk()


def discover_nodes():
    active_nodes = {}
    for host in utils.prs:
        name = utils.names[host]
        pw = utils.retrieve_credentials(host)
        status = utils.ssh_command(host,name,pw,'ping -c 1 1.1.1.1', False)
        for line in status.split('\n'):
            try:
                delta = line.split(' time=')[1]
                active_nodes[host] = float(delta.split(' ms')[0])
            except IndexError:
                pass
    return active_nodes


def nodeEvent(event):
    cx = event.x
    cy = event.y
    item = cv.find_closest(event.x, event.y)
    if item[0] in buttons:
        current_color = cv.itemcget(item, 'fill')

        if current_color == 'green':
            cv.itemconfig(item, fill='blue')
        else:
            cv.itemconfig(item, fill='green')
    print '%s,%s ' % (str(cx),str(cy))


def openFile():
    root.filename = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                                 filetypes=(("jpeg files", "*.jpg"),
                                                            ("all files", "*.*")))
    print (root.filename)


def addNode():
    host = str(raw_input('Enter IP: '))
    name = str(raw_input('Enter Username: '))
    # TODO: Get Password and use aes.py -d to add to KEYS/


def focus():
    print 'Clicked! Focus on'


def submit():
    cmd = v.get()
    print 'Command Window Contains:'
    print cmd
    entry.delete(0, len(list(cmd)))


w = 1200
h = 800
cv = Tk.Canvas(root, height=h, width=w)
cv.pack()

# Add Quit Button
button = Tk.Button(master=cv, text='Quit', command=sys.exit)
button.place(x=0, y=0, relwidth=0.07, relheight=0.06)

# Add a File/Help Menubar
menu = Tk.Menu(root)
root.config(menu=menu)
filemenu = Tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New Node", command=addNode)
filemenu.add_command(label="Open...", command=openFile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
helpmenu = Tk.Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)

# Add Title
title = Tk.Label(cv,text='P2P_CONTROL_DASHBOARD',bg='#00fff0')
title.place(x=w/2-150, h=0,relwidth=0.25, relheight=0.06)

# Discover nodes
nodes = discover_nodes()
colors = ['green','#00ff00']
handles = {}
index = 1
buttons = []
for node_handle in nodes.keys():
    x1 = 10
    y1 = index*100
    x2 = x1 + 100
    y2 = y1 + 50
    node_button = cv.create_rectangle(x1,y1,x2,y2,fill=colors[0], tags="clickable")
    node_title = cv.create_text((x2-x1)/2 + 10, y1+20, text=node_handle, font=("Papyrus", 10), fill='black')
    cv.bind(node_button, '<Button-1>', nodeEvent)
    index += 1
    buttons.append(node_button)
cv.bind('<Button-1>', nodeEvent)

# Add Command Window
v = Tk.StringVar()
entry_widget = Tk.Entry(master=cv)
box = Tk.Text(cv, height=10, width=50, bg='light gray')
entry = Tk.Entry(cv, width=65, bd=5, textvariable=v)
box.place(x=0, y=y2+50,relwidth=0.35,relheight=0.20)
entry.place(x=0, y=y2+30,relwidth=0.35,relheight=0.20)
execute = Tk.Button(master=cv, text='Submit', command=submit)
execute.place(x=0,y=y2+200,relwidth=0.1, relheight=0.1)

Tk.mainloop()
