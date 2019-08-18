from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import utils
import time
import sys
import os

tic = time.time()

if 'snap' in sys.argv:
    if len(sys.argv) <= 2:
        print 'Incorrect Usage!'
    if len(sys.argv) > 2:
        ip = sys.argv[2]
        host = utils.names[ip]
        pw = utils.retrieve_credentials(ip)
        snap_cmd = 'raspistill -t 1 -o test.jpeg; ls -la test.jpeg'
        utils.ssh_command(ip, host, pw, snap_cmd, False)
        os.system('sftp pi@%s:/home/pi/test.jpeg' % ip)
        os.system('python client.py cmd %s rm /home/pi/test.jpeg' % ip)
        print '\033[1m[%ss Elapsed]\033[0m' % str(time.time() - tic)
        print 'Opening Image...'
        os.system('eog test.jpeg')
        os.system('rm test.jpeg')


