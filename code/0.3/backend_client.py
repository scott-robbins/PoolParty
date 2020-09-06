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

class BackendClient:
	running = False

	def __init__(self):
		self.running = True

	def request_shares(self, peer_name, peer_ip):
		reply = ''
		api_request = '?SHARES :::: show'
		# TODO: ADD ENCRYPTION!!
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			reply = s.recv(65535)
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		self.client_socket.close()
		return reply
		

def main():
	client = BackendClient()

	if '-shares' in sys.argv and len(sys.argv) > 3:
		peer_name = sys.argv[2]
		peer_addr = sys.argv[3]
		remote_shares = client.request_shares(peer_name, peer_addr)
		print '%s has:\n%s' % (peer_name, remote_shares)

if __name__ == '__main__':
	main()
