from threading import Thread
import numpy as np
import engine
import utils
import time
import sys
import os

'''

'''


def distribute_file_resource(file_in):
    for peer in utils.prs:
        path = os.getcwd()+'/'+ peer
        cmd = Thread(target=utils.send_file,args=(path, peer, file_in))
        cmd.start()
        cmd.join()


tic = time.time()
if '-send_all_peers' in sys.argv and len(sys.argv) >= 3:
    file_in = sys.argv[2]
    distribute_file_resource(file_in)


print 'FINISHED [%ss Elapsed]' % str(time.time()-tic)
