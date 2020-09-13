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
	remote_stun = 54321
	local_stun = 12345
	share_port = 6969

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
		api_request = '*SHARES :::: %s ;;;; %s' % (self.name, fname)
		private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/'+self.name+'.pem').read())
		cipher_rsa = PKCS1_OAEP.new(private_key)
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			enc_sess_key = s.recv(2048) # Again, not sure why this occassionaly fails?
			sess_key = base64.b64decode(cipher_rsa.decrypt(enc_sess_key))
			reply = utils.DecodeAES(AES.new(sess_key), s.recv(65535))
			open(os.getcwd()+'/tmp.txt','wb').write(reply)
			chk_val = s.recv(1000)
			chk_sum = utils.cmd('sha256sum tmp.txt' , False).pop().split(' ')[0]
			os.remove('tmp.txt')
			if chk_val == chk_sum:
				print '[*] Checksums Match! Saving %s to shares' % fname
				open(os.getcwd()+'/PoolData/Shares/'+fname,'wb').write(reply)
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		s.close()
		return len(reply)

	def request_info(self, peer, peer_ip):
		reply = ''
		api_request = '?INFO :::: %s' % self.name
		private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/'+self.name+'.pem').read())
		cipher_rsa = PKCS1_OAEP.new(private_key)
		try:
			s = utils.create_tcp_socket(False)
			s.connect((peer_ip, 54123))
			s.send(api_request)
			enc_sess_key = s.recv(2048) # Again, not sure why this occassionaly fails?
			sess_key = base64.b64decode(cipher_rsa.decrypt(enc_sess_key))
			reply = utils.DecodeAES(AES.new(sess_key), s.recv(65535))
		except socket.error:
			print '[!!] Error making API request to %s' % peer_ip
			pass
		return reply

	def p2p_file_transfer(self, server_name, peer_name):
		ldate, ltime = utils.create_timestamp()
		sName, sIP, sPword, sPK = setup.load_credentials(server_name, False)
		pName, pIP, pPword, pPK = setup.load_credentials(peer_name, False)
		log_file = 'p2pDataFrom%s_%s_%s.p2p' % (peer_name, ldate.replace('/',''), ltime.replace(':',''))
		creds = 'sshpass -p "%s" ' % sPword
		print '[*] Dumping Direct Peer Transfer to %s' % log_file
		cmd = cred + 'ssh -L %d:localhost:%d  %s@%s nc -lp %d >> %s' %\
			(self.local_stun, self.remote_stun, sName, sIP, self.share_port, log_file)
		os.system(cmd)
		return log_file

	def upload_to_cloud(self):
		sName, sIP, sPword, sPK = setup.load_credentials('Server', False)
		share_path = '/root/PoolParty/code/0.3/PoolData/Shares'
		creds = 'sshpass -p "%s" ' % sPword
		cmd = creds + 'rsync -avzh PoolData/Shares %s' % share_path
		print '[*] Uploading Local Shares to %s' % share_path
		os.system(cmd)


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

	if '-info' in sys.argv and len(sys.argv) > 2:
		peer_name = sys.argv[2]
		hname, ip, pword, pkey = control.load_credentials(peer_name, False)
		print client.request_info(peer_name, ip)

	if '-p2p-recv' in sys.argv and len(sys.argv) > 3:
		srvr_name = sys.argv[2]
		peer_name = sys.argv[3]
		print '[*] Starting P2P File Transfer'
		client.p2p_file_transfer(srvr_name, peer_name)

	if '--upload' in sys.argv:
		client.upload_to_cloud()

if __name__ == '__main__':
	main()
