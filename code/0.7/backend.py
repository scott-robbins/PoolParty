from threading import Thread
import base64
import socket
import utils
import json
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
		self.actions = {'SHUTDOWN': self.kill,
						'SET_MASTER': self.add_master,
						'LIST_API': self.show_methods,
						'DUMP_TBL': self.dump_messenging_rules}
		# start the server
		self.run()

	def run(self):
		self.running = True
		self.runtime = time.time()
		sdate, stime = utils.create_timestamp()
		try:
			# create a socket 
			s = utils.create_tcp_listener(self.inbound)
			print('[*] Server Started [%s - %s]' % (sdate, stime))
			# Start Listening for Commands 
			while self.running:
				
				# accept a client
				client, cinfo = s.accept()
				# handle their request
				succeeded = False
				try:
					# event = pool.apply_async(self.client_handler, (client, cinfo))
					handler = Thread(target=self.client_handler, args=(client, cinfo))
					handler.start()

					succeeded = True
				except multiprocessing.TimeoutError:
					print('[!!] Connection Error with %s' % cinfo[0])
					pass
				# close everything
				client.close()
				# all incoming messages are from brokers 
				if succeeded and cinfo[0] not in self.brokers:
					self.brokers.append(cinfo[0])
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
		except socket.error:
			pass
		return csock

	def show_methods(self, cs, ca, req):
		result = utils.arr2str('-'.join(self.actions.keys()))
		cs.send(result)
		cs.close()

	def kill(self, cs, ca, req):
		print('\033[1m\033[31m[!!] Killing Backend Server\033[0m')
		self.running = False
		cs.send('[*] OK. Shutting Down Server')
		cs.close()

	def add_master(self, cs, ca, req):
		print('[!!] %s is replacing %s as Master Node' % (req, self.master))
		self.master = req
		cs.close()

	def dump_messenging_rules(self, cs, ca, req):
		rules = {'master': self.master_node,
				 'brokers': self.brokers}
		# dump this into /Config/Channels/Self/messaging.json
		with open('PoolData/Config/Channels/Self/messaging.json','w') as c:
					json.dump(rules, c)
		print('[*] Messaging rules saved')
		cs.close()



def main():
	if len(sys.argv) > 1:
		msgr = Messager(sys.argv[1])

if __name__ == '__main__':
	main()
