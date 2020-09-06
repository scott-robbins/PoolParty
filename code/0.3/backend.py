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

class BackendListener:
	inbound_port = 54123
	request_limit = 10
	running = False

	def __init__(self):
		self.serve_sock = self.create_server_socket()
		self.run()

	def create_server_socket(self):
		# Create a server socket (this one should support multi-threading)
		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("Socket created")
		try:
			soc.bind(('0.0.0.0', self.inbound_port))
		except:
			print("Bind failed. Error : " + str(sys.exc_info()))
			sys.exit()
		soc.listen(6) # queue up to 6 requests
		self.running = True
		return soc
   
  	def run(self):
  		start = time.time()
  		sdate, stime = utils.create_timestamp()
  		print '[*] Server Started [%s - %s]' % (sdate, stime)
  		try:
  			while self.running:
  				client, client_addr = self.serve_sock.accept()
  				Thread(target=client_handler, args=(client, client_addr)).start()
  		except KeyboardInterrupt:
  			print '[!!] Server Killed [Uptime %s seconds]' % (start - time.time())
  			self.running = False
  		self.serve_sock.close()

  	def client_handler(self, c, ci):
  		raw_req = c.recv(2046)
  		print 'Parsing API request from %s:%d' % (ci[0], ci[1])
  		api_req = raw_req.split(' :::: ')[0]
  		c.close()



def main():
	bas = BackendListener()	

if __name__ == '__main__':
	main()

