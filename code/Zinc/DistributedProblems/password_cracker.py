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
            if ''.join(list(guess)) == target_password:
                print 'CRACKED! [%ss Elapsed]' % str(time.time() - tic)
                CRACKED = True
    return CRACKED, guess


tic = time.time()


if '-single' in sys.argv:
    target_password = generate_random_password(n_words=1, salt_size=1)
    print 'Trying to crack password \033[1m%s\033[0m on \033[31mLocal Machine\033[0m' % \
          target_password
    words = utils.swap('words.txt', False)
    n_words = [1,1,1]
    salts = [1, 1, 1, 1, 1]
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
    target_password = generate_random_password(n_words=1, salt_size=1)
    print 'Trying to crack password \033[1m%s\033[0m on \033[31mLocal Machine\033[0m' % \
          target_password
    solved = False
    utils.distribute_file_resource('password_cracker.py')
    utils.distribute_file_resource('utils.py')
    cmd = 'python password_cracker.py -crack %s' % target_password
    utils.command_all_peers(cmd, True)
    while not solved:   # Poll machines for answer file?
        os.system('clear')
        print '\t \033[1m< \033[36mCRACKER\033[0m\033[1m >\033[0m'
        date, localtime = utils.create_timestamp()
        print 'RUNNING %s \t[%s - %s]' % (sys.argv[0], date, localtime)
        time.sleep(10)
        for ip in utils.prs:
            name = utils.names[ip]
            pw = utils.retrieve_credentials(ip)
            cmd = ''
            reply = utils.ssh_command(ip, name, pw, cmd, False)
            if 'answer.txt' in reply:
                print '\033[1m[!] \033[31mCRACKED\033[0m by %s \033[1m[%ss Elapsed]\033[0m' %\
                      (ip, str(time.time()-tic))
                utils.get_file_untrusted(ip, name, pw, 'answer.txt', True)
                solved = True
    print utils.swap('answer.txt', False).pop()

if '-crack' in sys.argv and len(sys.argv) == 3:
    target_password = sys.argv[2]
    print 'Trying to crack password \033[1m%s\033[0m on \033[31mLocal Machine\033[0m' %\
          target_password
    words = utils.swap('words.txt', False)
    n_words = [1, 1, 1]
    salts = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
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
        print '\033[1m[*] \033[3mProcess Killed \033[0m\033[1m[%ss Elapsed]\033[0m' % \
              str(time.time() - tic)
        exit()
    open('answer.txt', 'w').write(guess+'\n')
