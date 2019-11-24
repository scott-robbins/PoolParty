from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter as Tk
import tkFileDialog
import socket
import utils
import time
import sys
import os

root = Tk.Tk()
w = 1200;   h = 800
base = Tk.Canvas(root, height=h, width=w)
base.pack()

NAMES = []; PEERS = []; buttons = []


def discover_nodes():
    queued = ''
    addrs = []
    self = utils.get_local_ip()
    for i in range(2, 254):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(.25)
            s.connect(('192.168.1.%d' % i, 22))
            if self != '192.168.1.%d' % i:
                addrs.append('192.168.1.%d' % i)
            print '\033[1m\033[31m[*] \033[0m\033[1m192.168.1.%d Discovered\033[0m' % i
            s.close()
            queued += '192.168.1.%d\n' % i
        except socket.error:
            pass
            s.close()

    return addrs


def add_clock():
    # Get Date and Time for Clock Display
    date, localtime = utils.create_timestamp()
    timestamp = date + '\t' + localtime
    base.create_rectangle(425, 0, 730, 35, fill='#2200bf')
    base.create_text(575, 15, text=timestamp, font=('Papyrus', 12), fill='white')


def add_menu(fcns):
    # Add a File/Help Menubar
    menu = Tk.Menu(root)
    root.config(menu=menu)
    filemenu = Tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    for label in fcns.keys():
        filemenu.add_command(label=label, command=fcns[label])
        filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    helpmenu = Tk.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)


def choose_file():
    root.filename = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                                 filetypes=(("jpeg files", "*.jpg"),
                                                            ("python code", "*.py"),
                                                            ("all files", "*.*")))
    return root.filename


def send_file():
    target_file = choose_file()
    form = Tk.Toplevel(root)
    Tk.Label(form, text="Enter Peer Name: ").pack()
    e = Tk.Entry(form)
    e.pack(padx=5)

    def submit():
        addr = e.get()
        print 'Sending %s %s' % (addr, target_file)

        form.destroy()

    b = Tk.Button(form, text="Send", command=submit)
    b.pack(pady=5)


def node_event(event):
    cx = event.x
    cy = event.y
    item = base.find_closest(event.x, event.y)


def add_live_nodes():
    tic = time.time()
    global buttons, PEERS, NAMES
    nodes = discover_nodes()
    colors = ['green', '#00ff00']
    index = 0
    for node_handle in nodes:
        x1 = 10
        y1 = index * 110 + 5
        x2 = x1 + 100
        y2 = y1 + 50
        node_button = base.create_rectangle(x1, y1, x2, y2, fill=colors[0], tags="clickable")
        node_title = base.create_text(x1 + 50, y1 + 20, text=node_handle, font=("Papyrus", 10), fill='black')
        base.bind(node_button, '<Button-1>', node_event)
        index += 1
        buttons.append(node_button)

    base.bind('<Button-1>', node_event)
    print 'Nodes Linked [%ss Elapsed]' % str(time.time()-tic)


class AddToPool:
    def __init__(self, parent):
        top = self.top = Tk.Toplevel(parent)
        self.a = Tk.Label(top, text="Host Name").grid(row=0, column=0)
        self.b = Tk.Label(top, text="IP Address").grid(row=1, column=0)
        self.c = Tk.Label(top, text="Password").grid(row=2, column=0)
        self.a1 = Tk.Entry(top);    self.b1 = Tk.Entry(top);    self.c1 = Tk.Entry(top)
        # Place the forms fields into canvas
        self.a1.grid(row=0, column=1);  self.b1.grid(row=1, column=1);  self.c1.grid(row=2, column=1)
        # add submit button
        b = Tk.Button(top, text="Submit", command=self.write)
        b.grid(row=4, column=1)

    def write(self):
        global NAMES
        global PEERS
        host = self.a1.get()
        ip = self.b1.get()
        pw = self.c1.get()
        self.top.destroy()

        if ip not in NAMES.keys():
            print 'Adding %s@%s to nodes' % (host, ip)
            host_file = ip.replace('.', '') + '.txt'
            hkey_file = ip.replace('.', '') + '.key'
            os.system('python aes.py -e %s' % pw)
            os.system('mv encrypted.txt KEYS/%s' % host_file)
            os.system('mv key.txt KEYS/%s' % hkey_file)
            NAMES.keys().append(host)
            NAMES[host] = ip
            PEERS.append(ip)
            # check_nodes()
        else:
            print '[!!] %s is ALREADY a Peer' % ip


add_live_nodes()
add_menu({'Open': choose_file,
          'Send': send_file})
add_clock()
Tk.mainloop()
# EOF

