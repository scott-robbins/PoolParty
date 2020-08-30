import numpy as np
import control
import storage
import socket
import utils
import setup
import node
import time
import sys
import os

class BackendAPI:
	inbound = 54132
	running = True
	peers = {}
	network_name = ''
	def __init__(self):
		self.initialize()
		# define actions here
		self.run()

	def initialize(self):
		self.self_identify()
	
	def self_identify(self):
		# First need to establish identity
		if not os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			print '[!!] Cannot Start BackendAPI without setting up identity (see node.py)'
			if not os.path.isfile(os.getcwd()+'/PoolData/NX/requests.txt'):
				open(os.getcwd()+'/PoolData/NX/requests.txt', 'wb').write('? NAT Info\n')
			else:
				open(os.getcwd()+'/PoolData/NX/requests.txt', 'a').write('? NAT Info\n')
			exit() #  can ask master for it but probably cant continue?
		myaddr = utils.cmd('hostname -I',False).pop().split(' ')
        myaddr.pop(-1)
		# Load Peerlist
		for line in utils.swap(os.getcwd()+'/PoolData/NX/peerlist.txt', False):
			if len(line):
				peer = {}
				peer['netname']   = line.split(' ')[0]
				peer['hostname']  = line.split(' ')[1]
				peer['ipaddress'] = line.split(' ')[2]
				# choose self from peerlist
				if peer['ipaddress'] == myaddr:
					self.network_name = peer['ipaddress']
				else:
					self.peers[peer['ipaddress']] = peer


	def run(self):
		start_time = time.time()
		ldate, ltime = utils.create_timestamp()
		s = utils.create_tcp_socket(False)
		try:
			while self.running:
				client, caddr = s.accept()
				# Do something 
				client.close()
		except KeyboardInterrupt:
			self.running = False
			pass
		uptime = time.time() - start_time
		# close server socket when not running
		s.close()

def main():
	BackendAPI()

if __name__ == '__main__':
	main()

