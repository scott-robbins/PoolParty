import socket
import utils  
import setup
import time 
import sys
import os 

def update_peerdata():
	if not os.path.isdir('PoolData/Creds'):
		print '[!!] Credentials are missing'

def main():
	# IP Addresses change overtime, so peers need to be able to update their CRED 
	# registered in the database. 

	local_stun = 12345
	remote_stun = 54321
	shared_port = 6969
	if '--update' in sys.argv:
		update_peerdata()

	# Easy NAT using SSH Tunneling 
	if '--p2p-dump' in sys.argv and len(sys.argv) > 3:
		srvr = sys.argv[2]
		peer = sys.argv[3]
		srvName, srvIP, srvPword, srvPk = setup.load_credentials(srvr, False)
		ldate, ltime = utils.create_timestamp()
		log_file = 'p2pDataFrom%s_%s_%s.p2p' % (peer, ldate.replace('/',''), ltime.replace(':',''))
		cred = 'sshpass -p "%s" ' % srvPword
		cmd = cred + 'ssh -L %d:localhost:%d %s@%s nc -lvp %d >> %s' %\
		 (local_stun, remote_stun, srvName, srvIP, shared_port, log_file)
		print '[*] Remote Peer Can directly tunnel to you through port %d' % shared_port
		os.system(cmd)

	if '--p2p-chat' in sys.argv and len(sys.argv) > 3:
		srvr = sys.argv[2]
		peer = sys.argv[3]
		srvName, srvIP, srvPword, srvPk = setup.load_credentials(srvr, False)
		
		cred = 'sshpass -p "%s" ' % srvPword
		cmd = cred + 'ssh -L %d:localhost:%d %s@%s nc -lvp %d ' %\
		 (local_stun, remote_stun, srvName, srvIP, shared_port)
		print '[*] Remote Peer Can directly tunnel to you through port %d' % shared_port
		os.system(cmd)

if __name__ == '__main__':
	main()

