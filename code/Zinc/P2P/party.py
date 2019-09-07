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


if '-sum' in sys.argv and len(sys.argv) >=3:
    utils.get_sha256_sum(sys.argv[2], True)