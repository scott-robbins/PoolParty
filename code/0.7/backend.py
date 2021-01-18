import multiprocessing
import base64
import socket
import utils
import time
import sys 
import os

class Messager:
	inbound = 54123
	master_node = ''
	running = False
	runtime = 0.0
	brokers = []
	nx_name = ''

	def __init__(self, name):
		self.nx_name = name
		# Declare API Methods in the actions dict
		self.actions = {'SHUTDOWN': self.kill}
		# start the server
		self.run()

	def run(self):
		self.running = True
		self.runtime = time.time()
		pool = multiprocessing.Pool(3)
		sdate, stime = utils.create_timestamp()
		try:
			print('[*] Server Started [%s - %s]' % (sdate, stime))
			# Start Listening for Commands 
			while self.running:
				# create a socket 
				s = utils.create_tcp_listener(self.inbound)
				# accept a client
				client, cinfo = s.accept()
				# handle their request
				try:
					event = pool.apply_async(target=self.client_handler, args=(client, cinfo))
					client = event.get(timeout=10)
				except multiprocessing.TimeoutError:
					print('[!!] Connection Error with %s' % cinfo[0])
					pass
				# close everything
				client.close()
		except KeyboardInterrupt:
			self.running = False
			print('[*] Shutting Down Backend Messager')
			pass
		s.close()

	def client_handler(self, csock, caddr):
		try:
			# Get a raw request
			raw_req = csock.recv(1025)
			api_fun = raw_req.split(' ???? ')[0]
			api_req = raw_req.split(' ???? ')[1]
			# Determine if this is a valid request
			if api_fun not in self.actions.keys():
				csock.send(base64.b64encode('[!!] Unrecognized API Request'))
			else:
				# Handle the API request if it is known
				csock = self.actions[api_fun](csock, caddr, api_req)
		except SocketError:
			pass
		return csock

	def kill(self, cs, ca, req):
		print('\033[1m\033[31m[!!] Killing Backend Server\033[0m')
		self.running = False
		cs.send('[*] OK. Shutting Down Server')
		return cs



def main():
	if len(sys.argv) > 1:
		msgr = Messager(sys.argv[1])

if __name__ == '__main__':
	main()
