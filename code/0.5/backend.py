from threading import Thread
import network
import random
import utils 
import time
import sys
import os


class Backend():
	inbound  = 4242
	outbound = 9999
	running  = True
	masterIP = ''
	listener = []

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
			while self.running:
				self.listener = utils.create_tcp_listener(self.inbound)
				# accept inbound connection
				client, client_info = self.listener.accept()
				print(client_info)
				# check who the client is

				# move on 
				client.close()
		except KeyboardInterrupt:
			pass
			self.running = False
		# KILL SERVER 
		print('[*] Shutting down Server [%ss elapsed]' % str(time.time()-start))
		self.listener.close()