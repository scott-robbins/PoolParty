from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import base64
import socket
import utils
import time
import sys
import os


class API:
    commands = {}
    remote = ''
    port = 0
    session_token = ''

    def __init__(self, rmt, port):
        self.remote = rmt
        self.port = port
        self.session_token = self.get_token()

    def get_token(self):
        value = ''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.remote, self.port))
            s.send('?')
            value = s.recv(256)
            s.close()
        except socket.error:
            print '[!!] Connection Error'
            s.close()
            pass
        return value


if len(sys.argv) < 2:
    print 'Incorrect Usage!'
else:
    # Example
    agent = API(sys.argv[1], 12345)
