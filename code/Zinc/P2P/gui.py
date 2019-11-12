import Tkinter, Tkconstants, tkFileDialog
import subprocess as sub
import Tkinter as Tk
import numpy as np
import utils
import time
import sys
import os

tic = time.time()
''' Setup GUI Window '''
w = 1200
h = 800
root = Tk.Tk()
buttons = []
cv = Tk.Canvas(root, height=h, width=w)
cv.pack()

PEERS = utils.prs
NAMES = utils.names

window = Tk.Label(root,relief='sunken')
window.place(x=w/2, y=h/5, relwidth=0.3, relheight=0.4)


class SendFileDialog:
    def __init__(self, parent):
        top = self.top = Tk.Toplevel(parent)
        Tk.Label(top, text="Enter Remote Host:").pack()

        self.e = Tk.Entry(top)
        self.e.pack(padx=5)

        b = Tk.Button(top, text="Send", command=self.write)
        b.pack(pady=5)

    def write(self):
        addr = self.e.get()
        if os.path.isfile(os.getcwd()+'/enabled.txt'):
            os.remove('enabled.txt')
        open('enabled.txt', 'w').write(addr)
        self.top.destroy()


class GetFileDialog:
    def __init__(self, parent):
        top = self.top = Tk.Toplevel(parent)
        Tk.Label(top, text='Enter Remote Host:').pack()
        self.e = Tk.Entry(top)
        self.e.pack(padx=5)
        b = Tk.Button(top, text="Submit", command=self.write)
        b.pack(pady=5)

    def write(self):
        addr = self.e.get()
        file_name = 'get_file_host.txt'
        if os.path.isfile(os.getcwd()+'/'+file_name):
            os.remove(os.getcwd()+'/'+file_name)
        open(file_name, 'w').write(addr)
        self.top.destroy()


class AddToPool:
    def __init__(self, parent):
        top = self.top = Tk.Toplevel(parent)
        self.a = Tk.Label(top, text="Host Name").grid(row=0, column=0)
        self.b = Tk.Label(top, text="IP Address").grid(row=1, column=0)
        self.c = Tk.Label(top, text="Password").grid(row=2, column=0)
        self.a1 = Tk.Entry(top)
        self.b1 = Tk.Entry(top)
        self.c1 = Tk.Entry(top)
        # Place the forms fields into canvas
        self.a1.grid(row=0, column=1)
        self.b1.grid(row=1, column=1)
        self.c1.grid(row=2, column=1)
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
            add_live_nodes()
        else:
            print '[!!] %s is ALREADY a Peer' % ip


def discover_nodes():
    global NAMES
    global PEERS
    active_nodes = {}
    for host in utils.prs:
        name = NAMES[host]
        pw = utils.retrieve_credentials(host)
        status = utils.ssh_command(host,name,pw,'ping -c 1 1.1.1.1', False)
        for line in status.split('\n'):
            try:
                delta = line.split(' time=')[1]
                active_nodes[host] = float(delta.split(' ms')[0])
            except IndexError:
                pass
    return active_nodes


def node_event(event):
    cx = event.x
    cy = event.y
    item = cv.find_closest(event.x, event.y)
    if item[0] in buttons:
        current_color = cv.itemcget(item, 'fill')
        if current_color == 'green':
            cv.itemconfig(item, fill='blue')
        else:
            cv.itemconfig(item, fill='green')


def open_file():
    root.filename = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                                 filetypes=(("jpeg files", "*.jpg"),
                                                            ("python code", "*.py"),
                                                            ("all files", "*.*")))


def send_file():
    global buttons
    root.filename = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                                 filetypes=(("text files", "*.txt"),
                                                            ("python code", "*.py"),
                                                            ("jpeg files", "*.jpg"),
                                                            ("all files", "*.*")))
    if root.filename:
        SendFileDialog(root)
    # TODO: How to determine which node to send to?
    if os.path.isfile(os.getcwd()+'/enabled.txt'):
        recipient = utils.swap('enabled.txt', True).pop()
        print 'Sending %s to %d Recipients' % (root.filename, len(recipient))
        utils.send_file('',recipient,root.filename)


def get_file():
    global buttons
    GetFileDialog(root)
    try:
        remote = utils.swap('get_file_host.txt', True).pop()
        if remote:
            print 'Getting shared file list from remote host %s:~/PoolParty/code/Shared' % remote
            cmd = 'ls ~/PoolParty/code/'
            os.system('echo "'+cmd+'" >> tmp.sh')
            ''' Create Console/Command Window '''
            p = sub.Popen('sh ./tmp.sh', stdout=sub.PIPE, stderr=sub.PIPE)
            output, errors = p.communicate()
            text = Tk.Text(window)
            text.place(x=w/2,y=h/5,relwidth=0.3,relheight=0.3)
            text.insert(Tk.END, output)
            # reply = utils.ssh_command(remote, utils.names[remote],
            #                           utils.retrieve_credentials(remote), cmd, False)
            if 'Shared' in text.split('\n'):
                print '[*] Shared Folder Found'

            else:
                mk = 'mkdir ~/PoolParty/code/Shared'
                utils.ssh_command(remote, utils.names[remote],
                                  utils.retrieve_credentials(remote), mk, False)

    except:
        print '\033[1m[!!]\033[31m Something Went Wrong...\033[0m'
        os.remove('tmp.sh')


def add_node():
    # Create a form for user to fill in
    AddToPool(root)


def add_live_nodes():
    global buttons
    nodes = discover_nodes()
    colors = ['green', '#00ff00']
    index = 1
    for node_handle in nodes.keys():
        x1 = 10
        y1 = index * 100
        x2 = x1 + 100
        y2 = y1 + 50
        node_button = cv.create_rectangle(x1, y1, x2, y2, fill=colors[0], tags="clickable")
        node_title = cv.create_text((x2 - x1) / 2 + 10, y1 + 20, text=node_handle, font=("Papyrus", 10), fill='black')
        cv.bind(node_button, '<Button-1>', node_event)
        index += 1
        buttons.append(node_button)
    cv.bind('<Button-1>', node_event)


def add_clock():
    # Get Date and Time for Clock Display
    date, localtime = utils.create_timestamp()
    timestamp = date + '\t' + localtime
    cv.create_rectangle(425, 0, 730, 35, fill='#2200bf')
    cv.create_text(575, 15, text=timestamp, font=('Papyrus', 12), fill='white')


def add_menu():
    # Add a File/Help Menubar
    menu = Tk.Menu(root)
    root.config(menu=menu)
    filemenu = Tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New Node", command=add_node)
    filemenu.add_command(label="Open...", command=open_file)
    filemenu.add_command(label='Send File', command=send_file)
    filemenu.add_command(label='Get File', command=get_file)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    helpmenu = Tk.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)


def initialize():
    # Add Menu/Help Bar
    add_menu()

    # Add Quit Button
    button = Tk.Button(master=cv, text='Quit', command=sys.exit)
    button.place(x=0, y=0, relwidth=0.07, relheight=0.06)

    # Add a Clock to show date and time
    add_clock()


# Initialize The GUI Objects
initialize()


# Check Active Nodes, and add to GUI
add_live_nodes()


Tk.mainloop()
