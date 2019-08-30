from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import base64
import utils
import time
import sys
import os

token = base64.b64encode(get_random_bytes(16))
# Distributed File system needs to be based on hashing files
# and distributing those files to peers (2^N Peers will
# correspond to N Bytes of hash to use for sorting I guess?).


def get_sha256_sum(file_name, verbose):
    if os.path.isfile(file_name):
        os.system('sha256sum %s >> out.txt' % file_name)
        sum_data = utils.swap('out.txt', True).pop().split(' ')[0]
        if verbose:
            print sum_data
        return sum_data
    else:
        print '\033[1m[*] \033[31mCannot Find %s! \033[0m' % file_name
        return []


if '-sum' in sys.argv and len(sys.argv) >=3:
    get_sha256_sum(sys.argv[2], True)