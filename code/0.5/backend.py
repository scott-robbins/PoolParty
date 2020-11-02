from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from threading import Thread
import network
import random
import socket
import utils 
import time
import sys
import os


class Backend():
	inbound  = 4242
	outbound = 9999
	running  = True
	masterIP = ''
	session_key = ''
	private_key = ''

	def __init__(self, server):
		self.masterIP = server
		# check if any data already exists
		
		# if so, load as relevant
		# Start listening
		self.run()

	def initialize(self):
		# Create root folder if not present
		if os.path.isdir(os.getcwd()+'/PoolData'):
			os.mkdir(os.getcwd()+'/PoolData')
		# Create NodeInfo Folder
		if os.path.isdir(os.getcwd()+'/PoolData/Self'):
			os.mkdir(os.getcwd()+'/PoolData/Self')
		else:
			key_file = os.getcwd()+'/PoolData/Self/mykey.pem'
			if os.path.isfile(key_file):
				self.private_key = RSA.importKey(key_file.read().decode())


	def run(self):
		start = time.time()
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			pass
			print('[!!] Unable to create socket on 0.0.0.0:%d' % self.inbound)
			self.running = False
		try:
			s.bind(('0.0.0.0', self.inbound))
			s.listen(5)
		except socket.error:
			pass
			print('[!!] Connection Broken on 0.0.0.0:%d' % self.inbound)
			self.running = False
		try:
			cipher  = [];
			while self.running:
				# accept inbound connection
				client, client_info = s.accept()
				client_ip = client_info[0]
				client_port = client_info[1]
				# recieves first (encrypted)
				enc_request = s.recv(2048)
				# check who the client is
				if client_ip == self.masterIP:
					if not len(self.private_key):
						self.private_key = RSA.importKey(enc_request)
					else:
						req = PKCS1_OAEP.new(self.private_key).decrypt(enc_request).decode()
						print(req)
				# move on 
				client.close()
		except KeyboardInterrupt:
			pass
			self.running = False
		# KILL SERVER 
		print('[*] Shutting down Server [%ss elapsed]' % str(time.time()-start))
		self.listener.close()