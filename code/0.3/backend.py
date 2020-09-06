from threading import Thread
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

	def __init__(self, Node):
		self.node = Node
		# Initialize the backend based on type of node
		self.api = self.initialize()
		# define actions here
		self.run()

	def initialize(self):
		self.self_identify()
		api_methods = {}
		# if its a router node be sure to add NAT methods to backend 
		if self.node.ROUTER:
			api_methods{'NAT': self.nat_trav}
		# Add standard (common) functions
		return api_methods

	def nat_trav(self, c, ci, api_req):
		if '?' in api_req.split(' '):
			print '[*] %s is requesting NAT info for %s' % (ci[0], api_req.split('?')[1])
			# They are requesting NAT for another peer
			preq = api_req.split(' : ')[1]
			for line in open(os.getcwd()+'/PoolData/NX/natdat.txt', 'rb').readlines():
				name = line.split(':')[0]
				ext_ip = line.split(':')[1].replace(' ','').replace('\n','')
				if name == preq:
					c.send(line) # TODO: Add ecryption to API stuff???
		c.close()

	def share_hashlist(self, c, ci, api_req):
		req = api_req.split('?')
		c.close()
	
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
				raw_request = client.recv(65535)
				api_fcn = raw_request.split(' :::: ')[0]
				prequest = raw_request.split(' :::: ')[1]
				if api_fcn in self.api.keys():
					# client = self.api[api_fcn](client, caddr, raw_request.split(' :::: ')[1])
					cthread = Thread(target=self.api[api_fcn], args=(client, caddr, prequest))
					cthread.start()
				# client.close()
		except KeyboardInterrupt:
			self.running = False
			pass
		uptime = time.time() - start_time
		# close server socket when not running
		s.close()

class BackendClient:

	def __init__(self):
		self.server_name, self.server_addr, self.server_cred = utils.load_credentials('Server')
		self.identify()

	def identify(self):
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
				# peer = {}
				# peer['netname']   = line.split(' ')[0]
				# peer['hostname']  = line.split(' ')[1]
				# peer['ipaddress'] = line.split(' ')[2]
				# choose self from peerlist
				if line.split(' ')[2] == myaddr:
					self.network_name = line.split(' ')[2]


	def get_peer_ip(self, pname):
		c = utils.create_tcp_socket()
		c.connect((self.server_addr, 54123))
		c.send('NAT :::: ? %s' % pname)
		result = c.recv(1024)
		c.close()
		return result 

def main():
	if '-back' in sys.argv:
		BackendAPI(Node())

	if '-nat?' in sys.argv and len(sys.argv) > 2:
		peer_name = sys.argv[2]
		abc = BackendClient() # API Backend Client
		print abc.get_peer_ip(peer_name)

if __name__ == '__main__':
	main()

