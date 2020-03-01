from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter as Tk
import utils
import time
import sys
import os

tic = time.time()

snap_video = 'raspivid -o video_in.h264  -w 1280 -h 720 -t 8000'
snap_lapse = 'raspistill -t 8000 -tl 200 -o image%03d.png'
snap_stream = 'raspivid -t 0 -w 1280 -h 720 -fps 20 -o - | nc -l -p 6666'
recv_stream = 'mplayer -fps 200 -demuxer h264es ffmpeg://tcp://'
unpack_vid = 'ffmpeg -loglevel quiet -r 30 -i video_in.h264 -vcodec copy '
pack_vid = 'ffmpeg -i image%03d.png -c:v libx264 -vf fps=25 -pix_fmt yuv420p out.mp4'
clean_pics = "find -name '*.jpg' | cut -b 3- | while read n; do rm $n; done"


def on_click(event):
    if event.inaxes is not None:
        sp = [event.xdata, event.ydata]


def snap_save():
    if not os.path.isdir('PiCamImages'):
        os.mkdir('PiCamImages')
    date, localtime = utils.create_timestamp()
    tag = localtime.split(':')[0] + localtime.split(':')[1] + localtime.split(':')[2] + '_' + \
          date.split('/')[0] + date.split('/')[1] + date.split('/')[2]
    img_name = 'picam_' + tag + '.jpg'
    print 'Snapping %s' % img_name
    snap_cmd = 'raspistill -t 1 -o test.jpeg'
    ip = '192.168.1.229'
    host = utils.names[ip]
    pw = utils.retrieve_credentials(ip)
    utils.ssh_command(ip, host, pw, snap_cmd, False)
    os.system('sshpass -p %s sftp pi@%s:/home/pi/test.jpeg' % (pw, ip))
    os.system('python utils.py cmd %s "rm test.jpeg"' % ip)
    os.system('mv test.jpeg PiCamImages/%s' % img_name)
    print '\033[1m[%ss Elapsed]\033[0m' % str(time.time() - tic)
    return 'PiCamImages/'+img_name


if 'snap' in sys.argv:
    if len(sys.argv) <= 2:
        print 'Incorrect Usage!'
    if len(sys.argv) > 2:
        ip = sys.argv[2]
        host = utils.names[ip]
        pw = utils.retrieve_credentials(ip)
        snap_cmd = 'raspistill -t 1 -o test.jpeg'
        utils.ssh_command(ip, host, pw, snap_cmd, False)
        os.system('sshpass -p %s sftp pi@%s:/home/pi/test.jpeg' % (pw,ip))
        os.system('python utils.py cmd %s "rm test.jpeg"' % ip)
        print '\033[1m[%ss Elapsed]\033[0m' % str(time.time() - tic)
        print 'Opening Image...'
        os.system('eog test.jpeg')
        os.system('rm test.jpeg')

if 'monitor' in sys.argv:       # TODO: This looks really shitty...
    if len(sys.argv) <= 2:
        print 'Incorrect Usage!'
    if len(sys.argv) > 2:
        ip = sys.argv[2]
        host = utils.names[ip]
        pw = utils.retrieve_credentials(ip)
        snap_cmd = 'raspistill -t 1 -o test.jpeg; ls -la test.jpeg'
        utils.ssh_command(ip, host, pw, snap_cmd, False)
        os.system('sshpass -p %s sftp pi@%s:/home/pi/test.jpeg' % (pw, ip))
        os.system('python utils.py cmd %s "rm test.jpeg"' % ip)

        root = Tk.Tk()
        plt.style.use('dark_background')
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        a.imshow(plt.imread('test.jpeg'))


        def update():
            snap_cmd = 'raspistill -t 1 -o test.jpeg; ls -la test.jpeg'
            utils.ssh_command(ip, host, pw, snap_cmd, False)
            os.system('sshpass -p %s sftp pi@%s:/home/pi/test.jpeg' % (pw, ip))
            os.system('python client.py cmd %s "rm test.jpeg"' % ip)
            a.cla()
            im = plt.imread('test.jpeg')
            a.imshow(im - im.mean())


        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(f, master=root)
        plt.show()

        button = Tk.Button(master=root, text='Quit', command=sys.exit)
        button.place(x=0, y=0, relwidth=0.1, relheight=0.1)
        update = Tk.Button(master=root, text='Update', command=update)
        update.place(x=150, y=0, relwidth=0.1, relheight=0.1)

        canvas.draw()
        canvas.get_tk_widget().place(x=0, y=100, relwidth=1, relheight=0.8)
        canvas._tkcanvas.place(x=0, y=100, relwidth=1, relheight=0.8)

        f.canvas.callbacks.connect('button_press_event', on_click)
        Tk.mainloop()   # Lo        # T #

if 'stream' in sys.argv:
    ip = '192.168.1.229'
    host = utils.names[ip]
    pw = utils.retrieve_credentials(ip)
    utils.ssh_command(ip, host, pw, snap_stream, True)
    time.sleep(0.1)
    os.system('mplayer -fps 200 -demuxer h264es ffmpeg://tcp://192.168.1.229://6666')

if 'snap_save' in sys.argv:
    snap_save()

