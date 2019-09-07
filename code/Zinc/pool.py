from threading import Thread
import numpy as np
import engine
import utils
import time
import sys
import os

'''
I want to run a task as fast as possible. I have multiple machines who can
communicate at relatively quick speeds with pretty solid bandwidth. 

Can I find a way to achieve a task FASTER with this network, than with my single machine?
Let's find out!

[1] Super Basic Problem(s): 
    - the hash of every word in a fairly large dictionary? or every file in a shared folder?
[2] Somewhat hard Problem(s):
    - Processing a single object like a video in a frame by frame fashion
    - Analyzing a single song to generate a spectrogram or animated FFT
[3] Challenging to Make Parallel, and Challenging generally:
    - Computing a simulation and saving frames to a single video file
    - Solving an optimization of a single problem across nodes (find shortest path between
    a LARGE set of given verts and edges)
'''


def distribute_file_resource(file_in):
    for peer in utils.prs:
        path = os.getcwd()+'/'+ peer
        cmd = Thread(target=utils.send_file,args=(path, peer, file_in))
        cmd.start()
        cmd.join()


def dictionary_hash_bench(words, file_out):
    for word in words:
        os.system('')


tic = time.time()

# TODO: Solving [1] First!?
if '-self_bench':
    words = []
    for element in utils.swap('words.txt', False):
        words.append(element)
    print '%d Words Found [%ss Elapsed]' % (len(words), str(time.time() - tic))

if '-bench' in sys.argv:
    for word in words:
        os.system('')

if '-master' in sys.argv:
    distribute_file_resource('words.txt')
    distribute_file_resource('python pool.py')
    utils.command_all_peers('python pool.py -bench words.txt', True)

print 'FINISHED [%ss Elapsed]' % str(time.time()-tic)

