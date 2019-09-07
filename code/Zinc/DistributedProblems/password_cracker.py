from multiprocessing.pool import ThreadPool
from Crypto.Random import get_random_bytes
from threading import Thread
import numpy as np
import base64
import utils
import time
import sys
import os


def generate_random_password(n_words, salt_size):
    words = utils.swap('words.txt', False)
    random_words = np.random.random_integers(0, len(words), n_words)
    target = ''
    for e in random_words:
        target += words[e]
    target += base64.b64encode(get_random_bytes(salt_size))
    print 'The target password is \033[1m%s\033[0m' % target
    return target


def crack_thread(n_words, salts):
    CRACKED = False
    for N in n_words:
        for salt_len in salts:
            guess = ''
            random_indices = np.random.random_integers(0, len(words) - 1, N)
            for ii in random_indices:
                guess += words[ii]
            guess += base64.b64encode(get_random_bytes(salt_len))
            if guess == target_password:
                print 'CRACKED! [%ss Elapsed]' % str(time.time() - tic)
                CRACKED = True
    return CRACKED, guess


tic = time.time()
target_password = generate_random_password(1, 1)

if '-single' in sys.argv:
    print 'Trying to crack password on \033[31mLocal Machine\033[0m'
    words = utils.swap('words.txt', False)
    n_words = [1,1,1]
    salts = [1,1,1,1,1,1,1,1,1,1]
    CRACKED = False
    pool = ThreadPool(processes=4)
    try:
        while not CRACKED:
            async_result = pool.apply_async(crack_thread, (n_words, salts))
            CRACKED, guess = async_result.get()
            if CRACKED:
                print guess
                CRACKED = True
    except KeyboardInterrupt:
        CRACKED = True
        print '\033[1m[*] \033[3mProcess Killed \033[0m\033[1m[%ss Elapsed]\033[0m' % \
              str(time.time()-tic)

if '-multi' in sys.argv:
    print 'Trying to crack password on \033[31mMultiple Machines\033[0m'

