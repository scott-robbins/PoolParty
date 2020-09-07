from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from threading import Thread
import numpy as np
import control
import storage
import base64
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
		self.hname, self.ip, self.pword, self.pk = control.load_credentials(self.name, False)

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

	def request_shares(self, peer_name, peer_ip):
		reply = ''
		api_request = '?SHARES :::: %s ;;;; ' % self.name
		# TODO: ADD ENCRYPTION!!
		private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/'+self.name+'.pem').read())
		cipher_rsa = PKCS1_OAEP.new(private_key)
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			# enc_sess_key = s.recv(65535)
			enc_sess_key = s.recv(2048)
			# For some reason this occasionaly fails? They key comes across write as 256bytes it works 
			# but sometimes it comes in as 344bytes? no idea why, super confusing and unpredictable
			sess_key = base64.b64decode(cipher_rsa.decrypt(enc_sess_key))
			reply = utils.DecodeAES(AES.new(sess_key), s.recv(65535))
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		except ValueError:
			sess_key = base64.b64decode(cipher_rsa.decrypt(enc_sess_key))
			reply = utils.DecodeAES(AES.new(sess_key), s.recv(65535))
			pass
		s.close()
		return reply

	def request_file(self, fname, peer, peer_ip):
		reply = ''
		api_request = '*SHARES :::: %s ;;;; ' % self.name
		private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/'+self.name+'.pem').read())
		cipher_rsa = PKCS1_OAEP.new(private_key)
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			enc_sess_key = s.recv(2048) # Again, not sure why this occassionaly fails?
			sess_key = base64.b64decode(cipher_rsa.decrypt(enc_sess_key))
			reply = utils.DecodeAES(AES.new(sess_key), s.recv(65535))
			chk_val = s.recv(1000)
			open(os.getcwd()+'/PoolData/Shares/'+fname,'wb').write(reply)
			chk_sum = utils.cmd('sha256sum PoolData/Shares/%s' % fname, False).pop().split(' ')[0]
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		s.close()
		print 'Checksum Sent:\t%s' % chk_val
		print 'Checksum Local:\t%s' % chk_sum
		return reply, (chk_sum==chk_val)

def main():
	client = BackendClient()

	if '-shares' in sys.argv and len(sys.argv) > 2:
		peer_name = sys.argv[2];
		hname, ip, pword, pkey = control.load_credentials(peer_name, False)
		remote_shares = client.request_shares(peer_name, ip)
		print '%s has:\n%s' % (peer_name, remote_shares)

	if '-get' in sys.argv and len(sys.argv) > 3:
		peer_name = sys.argv[2];
		remote_file = sys.argv[3]
		hname, ip, pword, pkey = control.load_credentials(peer_name, True)
		file_data, file_hash = client.request_file(remote_file, peer_name, ip)
		print '[*] %d bytes transferred' % len(file_data)
		print file_hash

if __name__ == '__main__':
	main()
