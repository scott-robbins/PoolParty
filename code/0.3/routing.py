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
	# TODO: 
	# MESSAGES ARE NOT ENCRYPTED COMING ACROSS ONE HALF THOUGH BUT EASILY
	# COULD BE! 
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

	if '--p2p-send-shared' in sys.argv and len(sys.argv) > 2:
		file = sys.argv[2]
		sName, sIP, sWord, sKey = setup.load_credentials('Server', False)
		if not os.path.isfile(file):
			print '[!!] Cannot find %s' % file
			exit()
		# TODO; Encrypt it with personal key so identity is assured too
		cmd = 'cat %s | nc %s %d' % (file, sIP, shared_port)
		os.system(cmd)

	if '--p2p-send' in sys.argv and len(sys.argv) > 3:
		file = sys.argv[2]
		port = int(sys.argv[3])
		sName, sIP, sWord, sKey = setup.load_credentials('Server', False)
		if not os.path.isfile(file):
			print '[!!] Cannot find %s' % file
			exit()
		# TODO; Encrypt it with personal key so identity is assured too
		cmd = 'cat %s | nc %s %d' % (file, sIP, port)
		os.system(cmd)

	if '--sync-shares' in sys.argv:
		sName, sIP, sWord, sKey = setup.load_credentials('Server', False)
		creds = 'sshpass -p %s ' % sWord
		cmd = creds + 'rsync -azvh %s@%s:/root/PoolParty/code/0.3/PoolData/Shares PoolData/Shares' % (sName, sIP)
		os.system(cmd)

	if '--sync-routing' in sys.argv:
		sName, sIP, sWord, sKey = setup.load_credentials('Server', False)
		creds = 'sshpass -p %s ' % sWord
		cmd = creds + 'rsync -azvh %s@%s:/root/PoolParty/code/0.3/PoolData/NX PoolData/NX' % (sName, sIP)
		os.system(cmd)


if __name__ == '__main__':
	main()

