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
        self.port += 1
        return value

    def query_file_store(self):
        answer = ''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.remote, self.port))
            s.send('?{*f}'+self.session_token)
            answer = s.recv(1256)
            s.close()
        except socket.error:
            print '[!!] Connection Error'
            s.close()
            pass
        self.port += 1
        return answer

    def query_uptime(self, token):
        return self.request(token, self.remote, self.port, '?t'+token)

    def request(self, session_token, ip, port, cmd):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(cmd+session_token)
            answer = s.recv(1256)
            s.close()
        except socket.error:
            print '[!!] Connection Error'
            s.close()
            pass
        self.port += 1
        return answer


if len(sys.argv) < 2:
    print 'Incorrect Usage!'
else:
    # Example
    print 'Testing all API Queries...'
    agent = API(sys.argv[1], 12345)
    token = agent.query_file_store()
    print 'Session Token Recieved [%s]' % token
    uptime = agent.query_uptime(token)
    print 'Server uptime: %s' % uptime


