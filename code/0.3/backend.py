from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from threading import Thread
import numpy as np
import control
import storage
import socket
import base64
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
	session_keys = {}

	def __init__(self):
		self.serve_sock = self.create_server_socket()
		self.actions = {'?SHARES': self.show_shares,
						 '*SHARES': self.send_sharefile}
		self.run()

	def create_server_socket(self):
		# Create a server socket (this one should support multi-threading)
		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("Socket created")
		try:
			soc.bind(('0.0.0.0', self.inbound_port))
		except:
			print("[!!] Unable to Bind Socket. Error : " + str(sys.exc_info()))
			sys.exit()
		soc.listen(self.request_limit) # queue up to request limit
		self.running = True
		return soc
   
  	def run(self):
  		start = time.time()
  		sdate, stime = utils.create_timestamp()
  		print '[*] Server Started [%s - %s]' % (sdate, stime)
  		try:
  			while self.running:
  				client, client_addr = self.serve_sock.accept()
  				Thread(target=self.client_handler, args=(client, client_addr)).start()
  		except KeyboardInterrupt:
  			print '[!!] Server Killed [Uptime %s seconds]' % (time.time() - start)
  			self.running = False
  		self.serve_sock.close()

  	def client_handler(self, c, ci):
  		raw_req = c.recv(2046)
  		print 'Parsing API request from %s:%d' % (ci[0], ci[1])
  		api_req = raw_req.split(' :::: ')[0]
  		api_dat = raw_req.split(' :::: ')[1]
  		# API_DAT MUST REQUIRE NODES NAME TO LOAD CORRECT PUBLIC KEY FOR ENCRYPTION 
  		peer = raw_req.split(' :::: ')[1].split(' ;;;; ')[0].replace(' ','')
  		sess_id = '%s@%s' % (peer, ci[0])
  		if sess_id not in self.session_keys.keys():
  			print '[*] Assinging %s a new Session ID' % peer
  			self.session_keys[sess_id] = base64.b64encode(get_random_bytes(24))
  		n, i, pw, pk = control.load_credentials(peer, False)
  		cipher_rsa = PKCS1_OAEP.new(pk.publickey())
		enc_session_key = cipher_rsa.encrypt(sess_ids)
		c.send(enc_session_key)
  		# TODO: ADD ENCRYPTION TO API REQUESTS!!!!
  		if api_req in self.actions.keys():
  			# API functions must take these params and return client sock
  			c = self.actions[api_req](c, ci, api_dat)
  		
  		c.close()

  	def show_shares(self, c, ci, req_dat):
  		share_path = os.getcwd()+'/PoolData/Shares'
  		reply = ''
  		peer = req_dat.split(' ;;;; ')[0].replace(' ','')
  		sess_id = '%s@%s' % (peer, ci[0])
		key = base64.b64decode(self.session_keys[sess_id])
  		if not os.path.isdir(share_path):
  			reply += '0 Shared Files'
  		else:
  			contents, h = utils.crawl_dir(share_path, False, False)
  			reply += utils.arr2str(contents['file'])
  		# ADD ENCRYPTION TO API REQUESTS!!!!
  		c.send(utils.EncodeAES(AES.new(key), reply))
  		return c

  	def send_sharefile(self, c, ci, req_dat):
  		share_path = os.getcwd()+'/PoolData/Shares'
  		peer = req_dat.split(' ;;;; ')[0].replace(' ','')
  		sess_id = '%s@%s' % (peer, ci[0])
  		key = base64.b64decode(self.session_keys[sess_id])
  		if req_dat in os.listdir(share_path):
  			file_data = open(share_path+'/'+req_dat, 'rb').read()
  		else:
  			file_data = 'Unable to find %s' % req_dat
  		# ADD ENCRYPTION TO API REQUESTS !!!!
  		# c.send(file_data)
  		c.send(utils.EncodeAES(AES.new(key), file_data))
  		return c


def main():
	bas = BackendListener()	

if __name__ == '__main__':
	main()

