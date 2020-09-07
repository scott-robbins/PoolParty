from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from threading import Thread
import numpy as np
import control
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
		self.identify()
		self.node = node.Node(self.name)
		self.serve_sock = self.create_server_socket()
		self.actions = {'?SHARES':  self.show_shares,
						 '*SHARES': self.send_sharefile,
						 '?INFO': self.show_node_info}
		self.run()

	def identify(self):
		int_ip = utils.cmd('hostname -I', False).pop().replace('\n','').replace(' ','')
		hname = utils.cmd('whoami', False).pop().replace('\n','').replace(' ','')
		
		if not os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			print '[!!] Unable to load credentials'
			exit()
		else:
			for line in open(os.getcwd()+'/PoolData/NX/peerlist.txt', 'rb').readlines():
				line = line.replace('\n', '')
				data = line.split(' ')
				
				if data[1].replace(' ','') == hname and data[2].replace(' ','') == int_ip:
					self.name = data[0].replace(' ','')
					print '[*] Starting BackendClient as %s' % self.name
					break
				else:
					print hname
					print int_ip
					print data[1].replace(' ', '')
					print data[2].replace(' ', '')

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
  		k = base64.b64encode(get_random_bytes(16))
  		n, i, pw, pk = control.load_credentials(peer, False)
		enc_session_key = PKCS1_OAEP.new(pk.publickey()).encrypt(k)
		c.send(enc_session_key)
  		if api_req in self.actions.keys():
  			# API functions must take these params and return client sock
  			c = self.actions[api_req](c, ci, api_dat, k)
  		c.close()

  	def show_shares(self, c, ci, req_dat, key):
  		share_path = os.getcwd()+'/PoolData/Shares'
  		reply = ''
  		peer = req_dat.split(' ;;;; ')[0].replace(' ','')
  		sess_id = '%s@%s' % (peer, ci[0])
  		if not os.path.isdir(share_path):
  			reply += '0 Shared Files'
  		else:
  			contents, h = utils.crawl_dir(share_path, False, False)
  			reply += utils.arr2str(contents['file'])
  		# ADD ENCRYPTION TO API REQUESTS!!!!
  		c.send(utils.EncodeAES(AES.new(base64.b64decode(key)), reply))
  		return c

  	def send_sharefile(self, c, ci, req_dat, key):
  		share_path = os.getcwd()+'/PoolData/Shares'
  		peer = req_dat.split(' ;;;; ')[0].replace(' ','')
  		rmt_file = req_dat.split(' ;;;; ')[1]
  		if os.path.isfile(share_path+'/'+rmt_file):
  			file_data = open(share_path+'/'+rmt_file, 'rb').read()
  		else:
  			file_data = 'Unable to find %s' % rmt_file
  		# ADD ENCRYPTION TO API REQUESTS !!!!
  		# c.send(file_data)
  		c.send(utils.EncodeAES(AES.new(base64.b64decode(key)), file_data))
  		chk_sum = utils.cmd('sha256sum PoolData/Shares/%s' % rmt_file, False).pop().split(' ')[0]
  		c.send(chk_sum)
  		return c

  	def show_node_info(self, c, ci, req_dat, key):
  		info = self.node.show()
  		c.send(utils.EncodeAES(AES.new(base64.b64decode(key)), info))
  		return c

def main():
	bas = BackendListener()	

if __name__ == '__main__':
	main()

