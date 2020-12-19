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
		self.initialize()
		# Setup Folders/Files 
		self.setup_folders()
		self.serve = []
		# Define Server Actions 
		self.actions = {'UPTIME': self.uptime,
						'PEERS': self.query_peerlist,
						'SHARES': self.query_shares,
						'FILE?': self.query_file,
						'NSHARES': self.query_nshares,
						'CODEUPDATE': self.update_code,
						'COMMANDS': self.list_commands,
						'EXEC':	self.execute}
		# Start Background Tasks
		# Create Listener 
		print('\033[1m\033[33m[*] %s - %s: Starting Server\033[0m' % (self.start_date, self.start_time))
		# Start listening for API Requests
		self.run()

	def initialize(self):
		h,e,i,s = setup.load_local_vars()
		self.info['host'] 		= h
		self.info['external'] 	= e
		self.info['internal']	= i
		self.info['server']		= s
		self.RUNNING = True
		self.start_date, self.start_time = utils.create_timestamp()

	def setup_folders(self):
		if not os.path.isdir(os.getcwd()+'/.PoolData'):
			os.mkdir('.PoolData')
		if not os.path.isdir(os.getcwd()+'/.PoolData/Shares'):
			os.mkdir('.PoolData/Shares')
		if not os.path.isdir(os.getcwd()+'/.PoolData/Work'):
			os.mkdir('.PoolData/Work')
		# TODO: Backend Should do logging on requests made by clients

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
				try:
					api_var = raw_req.split(api_fcn)[1:]
				except IndexError:
					print('Unparsable request: %s' % raw_req)
					unhandled = False
					break
				# handle the request
				if api_fcn in self.actions.keys():
					log = '\033[1m\033[35m[*]\033[0m\033[1m' 
					log += '\033[36m %s \033[0m\033[1m\033[35mis making ' % (info[0])
					log += '\033[37m%s \033[0m\033[1m\033[35mrequest\033[0m' % api_fcn
					print(log)
					s = self.actions[api_fcn](s, info, api_var)
					unhandled = False
				else:
					s.send('\033[31m\033[1m[!!] Invalid API Request\033[0m')
					unhandled = False

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

	def list_commands(self, csock, caddr, api_req):
		cmds = self.actions.keys()
		csock.send('Commands:\n%s' % utils.arr2str(cmds))
		return csock

	def query_peerlist(self,csock,caddr,api_req):
		msg = 'Peer List:\n'
		msg += utils.arr2str(self.peers)
		csock.send(msg)
		return csock

	def query_nshares(self, csock, caddr, api_req):
		n_files = len(os.listdir(os.getcwd()+'/.PoolData/Shares'))
		msg = '[*] %d shares available' % n_files
		csock.send(msg)
		return csock

	def query_shares(self, csock, caddr, api_req):
		file_list = os.listdir(os.getcwd()+'/.PoolData/Shares')
		msg = 'Shared Files on %s@%s:\n' % (self.info['host'], self.info['internal'])
		msg += utils.arr2str(file_list)
		csock.send(msg)
		return csock

	def query_file(self, csock, caddr, api_req):
		if len(api_req.split('?')) > 1:
			file_name = api_req.split('?')[0]
			req = api_req.split('?')[1]
		# make sure file exists
		try:
			if req == 'SIZE':
				sz = os.path.getsize(os.getcwd()+'/.PoolData/Shares/%s' % file_name)
				reply = '%s is %d bytes, and was last modified %s'
				csock.send(reply % (file_name, sz, utils.cmd('date -r '+os.getcwd()+'/.PoolData/Shares/%s' % file_name)))
			if req == 'DATA':
				csock.send(open(os.getcwd()+'/.PoolData/Shares/%s' % file_name,'rb').read())
		except OSError:
			csock.send('Sorry, something went wrong handling <%s>' % api_req)

		return csock

	def update_code(self, csock,caddr, api_req):
		update_cmd = 'cd ..; bash update.sh'
		os.system(update_cmd)
		return csock

	def execute(self, csock, caddr, api_req):
		op_cmd = api_req[0].split(' :::: ')[1].split(' ')[0]
		try:
			payload = utils.arr2chr(api_req[0].split(op_cmd)[1:])
		except IndexError:
			payload = ''
			pass
		allowed_ops = {'python', 'java', 'bash'}
		if op_cmd in allowed_ops:
			# TODO: Create something to handle each op type 
			# execute the function/program and monitor it's 
			# status and completion.
			# print('Executing %s%s' % (op_cmd, payload))
			if op_cmd == 'bash':
				c = '%s' % payload
				print('Executing:\n$%s' % c)
				os.system(c)
				csock.send(result)
		else:
			print('Got OP: %s' % op_cmd)
			print('Got Payload: %s' % payload)
		return csock

	def shutdown(self):
		ldate, ltime = utils.create_timestamp()
		uptime = time.time() - self.start
		try:
			self.serve.close()
		except socket.error:
			pass
		print('\033[1m\033[31m\n[*] %s - %s: Shutting Down Server [Uptime: %fs]\033[0m' %(ldate, ltime, uptime))
		return uptime




def main():
	listener = Backend()

if __name__ == '__main__':
	main()
