from threading import Thread
import network
import random
import socket
import setup
import utils
import time
import sys 
import os


class Backend():
	INBOUND = 54123
	# RUNNING = False
	start_date = ''
	start_time = ''
	start  = 0.0
	peers = []
	info = {}
	actions = {}

	def __init__(self):
		# Load Local Variables 
		h,e,i,s = setup.load_local_vars()
		self.info['host'] 		= h
		self.info['external'] 	= e
		self.info['internal']	= i
		self.info['server']		= s
		self.RUNNING = True
		self.start_date, self.start_time = utils.create_timestamp()
		# Setup Folders/Files 
		self.serve = []
		# Define Server Actions 
		self.actions = {'UPTIME': self.uptime,
						'PEERS': self.query_peerlist}
		# Start Background Tasks
		# Create Listener 
		print('\033[1m[*] %s - %s: Starting Server\033[0m' % (self.start_date, self.start_time))
		# Start listening for API Requests
		self.run()

	def setup_folders(self):
		if not os.path.isdir(os.getcwd()+'/.PoolData'):
			os.mkdir('.PoolData')
		if not os.path.idir(os.getcwd()+'/.PoolData/Shares'):
			os.mkdir('.PoolData/Shares')
		if not os.path.idir(os.getcwd()+'/.PoolData/Work'):
			os.mkdir('.PoolData/Work')


	def run(self):
		self.start = time.time()
		self.serve = utils.create_tcp_listener(self.INBOUND)
		try:
			while self.RUNNING:
				# Wait for incoming requests 
				client, caddr = self.serve.accept()
				if caddr[0] not in self.peers:
					self.peers.append(caddr[0])
				# handle incoming request
				status = self.client_handler( client, caddr)
				
		except KeyboardInterrupt:
			self.RUNNING = False
			pass

		# Shutdown the server
		return self.shutdown()

	def client_handler(self,s, info):
		result = ''; unhandled = True
		try:
			while unhandled:
				# get the api request
				raw_req = s.recv(2048)
				# check for valid request
				if len(raw_req.split(' :::: '))<2:
					s.send('[!!] Invalid API Request')
					unhandled = False
				# parse the request 
				api_fcn = raw_req.split(' :::: ')[0]
				api_var = raw_req.split(' :::: ')[1]
				if api_fcn in self.actions.keys():
					print('[*] %s is making a %s request' % (info[0], api_fcn))
					s = self.actions[api_fcn](s, info, api_var)
					unhandled = False
				else:
					s.send('[!!] Invalid API Request')
					unhandled = False
			result = s.recv(2048)
			# when finished close the socket
			s.close()
		except socket.error as e:
			pass
		return result

	def uptime(self, csock, caddr, api_req):
		up = time.time() - self.start
		msg = 'Starting at %s - %s, uptime is %d seconds.' % (self.start_date,self.start_time,up)
		csock.send(msg)
		return csock

	def query_peerlist(self,csock,caddr,api_req):
		msg = 'Peer List:\n'
		msg += utils.arr2str(self.peers)
		csock.send(msg)
		return csock

	def query_nshares(self. csock, caddr, api_req):
		n_files = len(os.listdir(os.getcwd()+'/.PoolData/Shares'))
		msg = '[*] %d shares available' % n_files
		csock.send(msg)
		return csock


	def shutdown(self):
		ldate, ltime = utils.create_time_stamp()
		uptime = time.time() - self.start
		try:
			self.serve.close()
		except socket.error:
			pass
		print('[*] %s - %s: Shutting Down Server [Uptime: %ds]' %(ldate, ltime))
		return uptime




def main():
	listener = Backend()

if __name__ == '__main__':
	main()
