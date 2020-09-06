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
		self.identify()
		self.hname, self.ip, self.pword, self.pk = control.load_credentials(self.name, True)

	def identify(self):
		int_ip = utils.cmd('hostname -I', False).pop().replace('\n','')
		hname = utils.cmd('whoami', False).pop().replace('\n','')
		
		if not os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			print '[!!] Unable to load credentials'
			exit()
		else:
			for line in open(os.getcwd()+'/PoolData/NX/peerlist.txt', 'rb').readlines():
				line = line.replace('\n', '')
				data = line.split(' ')
				
				if data[1].replace(' ','') == hname and data[2].replace(' ','') == int_ip:
					self.name = data[0]
					print '[*] Starting BackendClient as %s' % self.name
					break
				# else:
				# 	print '%s != %s ? [%s]' % (data[2], int_ip, str(data[2]==int_ip))

	def request_shares(self, peer_name, peer_ip):
		reply = ''
		api_request = '?SHARES :::: %s ;;;;' % self.name
		# TODO: ADD ENCRYPTION!!
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			reply = s.recv(65535)
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		s.close()
		return reply
		

def main():
	client = BackendClient()

	if '-shares' in sys.argv and len(sys.argv) > 2:
		peer_name = sys.argv[2];
		hname, ip, pword, pkey = control.load_credentials(peer_name, True)
		remote_shares = client.request_shares(peer_name, ip)
		print '%s has:\n%s' % (peer_name, remote_shares)

	if '-get' in sys.argv and len(sys.argv) > 2:
		peer_name = sys.argv[2];
		hname, ip, pword, pkey = control.load_credentials(peer_name, True)
		

if __name__ == '__main__':
	main()
