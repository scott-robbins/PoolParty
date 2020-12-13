from threading import Thread
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
        status = utils.ssh_command(host,name,pw,'ping -c 1 1.1.1.1', False)
        for line in status.split('\n'):
            try:
                delta = line.split(' time=')[1]
                active_nodes[host] = float(delta.split(' ms')[0])
            except IndexError:
                pass
    return active_nodes

nodes = discover_nodes()

w = 800
h = 800
root = Tk.Tk()
tic = time.time()
buttons = []
canvas = Tk.Canvas(root, height=h, width=w)
Tk.Label(canvas,)
canvas.pack()
border = canvas.create_rectangle(30, 30, 600, 600, fill='#000000')

bars = {}
index = 0
for n in nodes.keys():
    pad = 50 * index + 50
    y1 = 150 * index
    x1 = 40
    y2 = y1 + 50
    x2 = x1 + 100
    y1 += pad
    y2 += pad
    node_transfer_speed_kbs = utils.test_transfer_rate(n)
    a = canvas.create_rectangle(x2 + 15, y1, x2 + 110 + 50 * int(node_transfer_speed_kbs / 25), y2, fill='#ff0000')
    b = canvas.create_text(x2 + 55, y1 + (y2 - y1) / 2, fill='#ffffff', text='TX Speed', font=("Papyrus", 10))
    bars[n] = [a, b]
    index += 1


def nodeEvent(event):
    cx = event.x
    cy = event.y
    item = canvas.find_closest(event.x, event.y)
    if item[0] in buttons:
        current_color = canvas.itemcget(item, 'fill')

        if current_color == 'green':
            canvas.itemconfig(item, fill='blue')
        else:
            canvas.itemconfig(item, fill='green')
    # print '%s,%s ' % (str(cx),str(cy))


def addLiveNodesToGUI():
    global buttons
    nodes = discover_nodes()
    colors = ['green', '#00ff00']
    index = 0
    for node_handle in nodes.keys():
        pad = 50*index+50
        y1 = 150*index
        x1 = 40
        y2 = y1 + 50
        x2 = x1 + 100
        y1 += pad
        y2 += pad
        node_button = canvas.create_rectangle(x1, y1, x2, y2, fill=colors[0], tags="clickable")
        node_title = canvas.create_text(x1+(x2-x1)/2, y1 + 20, text=node_handle, font=("Papyrus", 10), fill='black')
        e = Tk.Entry(canvas, width=50)
        e.place(x=(x2-x1)/2-5, y=y2 + 10, relwidth=0.2, relheight=0.1)
        canvas.bind(node_button, '<Button-1>', nodeEvent)
        index += 1
        buttons.append(node_button)
    canvas.bind('<Button-1>', nodeEvent)


def show_connectivity():
    global bars
    index = 0
    for node_handle in nodes.keys():
        pad = 50 * index + 50
        y1 = 150 * index
        x1 = 40
        y2 = y1 + 50
        x2 = x1 + 100
        y1 += pad
        y2 += pad
        try:
            canvas.delete(bars[node_handle][0])
            canvas.delete(bars[node_handle][1])
        except:
            pass
        node_transfer_speed_kbs = utils.test_transfer_rate(node_handle)
        a = canvas.create_rectangle(x2 + 15, y1, x2 + 100 + 100 * int(node_transfer_speed_kbs / 25), y2, fill='#ff0000')
        b = canvas.create_text(x2 + 55, y1 + (y2 - y1) / 2, fill='#ffffff', text='TX Speed', font=("Papyrus", 10))
        bars[node_handle] = [a, b]
        index += 1
    return bars

# live_peers = discover_nodes()
addLiveNodesToGUI()
root.after(5000, show_connectivity)
Tk.mainloop()
