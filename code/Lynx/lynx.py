from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import random
import base64
import socket
import utils
import time
import sys
import os

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING        # pad the text to be encrypted
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))            # encrypt with AES, encode with base64
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

date, localtime = utils.create_timestamp()


class TestServer:
    clients_seen = {}
    actions = {'?': base64.b64encode(get_random_bytes(128)),
               '?{*f}': utils.cmd('ls')}
    inbound_port = 12345
    outgoin_port = 12346
    tic = 0.0

    def __init__(self):
        self.init()

    def init(self,):
        # Make sure you have the correct permissions
        if os.getuid() != 0:
            print '[!!] Not running as root'
            exit()
        self.running = True
        try:
            runtime = self.run()
        except KeyboardInterrupt:
            print '[*] Killing Server!'
            print '[* Server Killed After %s seconds *]' % str(runtime)
            self.running = False
            # TODO: Dump unlogged data
            exit()

    def run(self):
        print '[*] Server Started %s - %s [*]' % (date, localtime)
        self.tic = time.time()
        while self.running:
            try:
                '''                  Socket Setup                 '''
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', self.inbound_port))
            except socket.error:
                print 'Cannot Assign bind socket'
                s.close()
                time.sleep(10)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', self.inbound_port))

            s.listen(5)
            '''                  Client/Event Handling        '''
            client_sock, addr = s.accept()
            print '[*] Connection Accepted from %s:%d' % (addr[0], addr[1])
            client_query = client_sock.recv(1024)
            if client_query in self.actions.keys():
                reply = self.actions[client_query]
                print '[$] %s => %s' % (client_query, reply)
                client_sock.send(reply)
                client_sock.close()
            if client_query == '?':
                self.clients_seen[addr[0]] = reply
        return time.time()-self.tic

    def get_uptime(self):
        return time.time()-self.tic


TestServer()
