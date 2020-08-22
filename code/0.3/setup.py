from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import numpy as np
import base64
import socket
import utils
import time
import sys 
import os

def add_client_cmdline():
	if not os.path.isdir(os.getcwd()+'/PoolData/'):
		os.mkdir(os.getcwd()+'/PoolData')
	uname, password = create_credentials()
	return uname

def create_credentials():
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		os.mkdir(os.getcwd()+'/PoolData/Creds')
	
	# Make sure username doesn't already exist, otherwise try again
	added = False
	while not added:
		uname = raw_input('Enter PoolParty Username:\n')
		hname = raw_input('Enter Hostname:\n')
		created, password = create_password()
		if not created:
			print '[!!] Unable to create password'
			exit()
		newcred = '%s.pem' % uname
		existing = os.listdir(os.getcwd()+'/PoolData/Creds')
		if newcred not in existing:
			# Save Them, Encrypted with private key (also saved)
			key = RSA.generate(2048)
			private_key = key.exportKey()
			public_key = key.publickey()
			file_out = open(os.getcwd()+"/PoolData/Creds/%s.pem" % uname, "wb")
			file_out.write(key.exportKey('PEM'))
			file_out.close()
			ip_addr = raw_input('Enter IP Address to use when adding this user to Pool:\n')

			# Encrypt the session key with the public RSA key
			cipher_rsa = PKCS1_OAEP.new(public_key)
			cred_file_dat = b'%s@%s:%s' % (uname, ip_addr, password)
			enc_cred_data = cipher_rsa.encrypt(cred_file_dat)
			fname = '%s@%s' % (uname, hname)
			open(os.getcwd()+'/PoolData/Creds/%s.creds' % fname, 'wb').write(enc_cred_data)
			added = True
		else:
			print 'Username %s is already taken!. Try Again.' % uname

	return uname, password	

def create_password():
	matched = False
	password = ''
	attempts =  0
	while not matched and attempts < 3:
		cmd = "#!/bin/bash\n echo 'Enter Password:'; read -s PASS; echo $PASS >> cmd.txt\n#EOF"
		open('tmp.sh','wb').write(cmd)
		os.system('bash tmp.sh; rm tmp.sh')
		password = utils.swap('cmd.txt', True).pop()
		# Double Check it twice before creating 
		cmd2 = "#!/bin/bash\n echo 'Re-Enter Password:'; read -s PASS; echo $PASS >> cmd.txt\n#EOF"
		open('tmp.sh','wb').write(cmd2)
		os.system('bash tmp.sh; rm tmp.sh')
		password_check = utils.swap('cmd.txt', True).pop()
		if password == password_check:
			print '[*] Username and Password Created'
			matched = True
		elif (len(password) > 7):
			print '[x] Password must be longer than 7 Characters!'
		else:
			print '[X] The two password entries did not match!'
		attempts += 1
	return matched, password

def load_credentials(nickname, debug):
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		print '[!!] No credentials Found. Plese Register First!'
		exit()
	found = False
	host  = ''
	key_name = nickname+'.pem'
	for name in os.listdir('PoolData/Creds'):
		if len(name.split('@'))==2:
			if nickname == name.split('@')[0]:
				if debug:
					print '[*] Found Credentials for %s' % nickname
				cred_name = name
				host = name.split('@')[1].split('.creds')[0]
				found = True
	if not found:
		print '[!!] Unable to find username %s' % nickname
		exit()
	if not os.path.isfile(os.getcwd()+'/PoolData/Creds/%s' % key_name):
		print '[!!] No credentials founder for username %s' % host
		exit()
	
	private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/%s' % key_name).read())
	raw_creds = PKCS1_OAEP.new(private_key).decrypt(open(os.getcwd()+'/PoolData/Creds/%s' % cred_name,'rb').read())
	hostname = raw_creds.split('@')[0]
	ip_addr = raw_creds.split('@')[1].split(':')[0]
	password = raw_creds.split(':')[1]
	return host, ip_addr, password, private_key

def check_pooldeck():
	exists = False
	if os.path.isdir(os.getcwd()+'/PoolData'):
		if os.path.isdir(os.getcwd()+'/PoolData/Creds'):
			exists = True
	return exists

def test_cnx(pool_name):
	connected = False
	hostname, ip, passwd, pk = load_credentials(pool_name, False)
	start = time.time()
	# Test Command Execution on the remote machine with simple hostname check
	result = utils.ssh_exec('whoami',ip,hostname,passwd,False).replace('\n','')
	if result == hostname:
		connected = True
	# Record how long it took to get a reply from this command
	dt = time.time() - start
	return dt, connected

def test_pool():
	# Get All Nodes listed in creds
		nodes = list(set(utils.cmd('ls PoolData/Creds/*.creds', False)))
		timing = {}
		# run a connection check for each
		for name in nodes:
			n = name.split('/').pop(-1).split('@')[0]
			ping, cnx = test_cnx(n)
			if cnx:
				# color the print out based on reply speed
				if ping <= 0.75:
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.GREEN, ping,utils.FEND)
				if 0.75 < ping < 1.5:
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.YELLOW, ping,utils.FEND)
				if 1.5 < ping :
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.YELLOW, ping,utils.FEND)
				timing[ping] = n
		# also calculate fastest
		best_time = np.min(list(set(timing.keys())))
		best_node = timing[best_time]

		# report connectivity
		print '[*] %s is fastest' % best_node
		return best_node, best_time

def usage():
	print '[!!] Incorrect usage [!!]\n'
	print '$ python setup.py <opt> <args>\n'
	print 'Valid options are:'
	opts = ['-add', '-load', '-cmd_rmt', '-pool_cnx']
	info = {'-add': 'Add peer to network',
			'-load': 'Load Credentials for a node',
			'-cmd_rmt': 'Execute command on remote node',
			'-pool_cnx': 'Check pool connectivity/network connections'}
	for o in opts:
		print '\t-%s    \t(%s)' % (o, info[o])

def main():
	DEBUG = False
	completed = False

	if ('--add' or '--add_cmd') in sys.argv:
		completed = True
		new_client = add_client_cmdline()
		# Test that those creds work!!
		delta, is_connected = test_cnx(new_client)
		if not is_connected:
			print '[!!] Unable to connect to Peer'
		else:
			print '[*] Successfully added Peer'
			# download the github repo here
			git_get = 'python setup.py --cmd_rmt %s git clone https://github.com/scott-robbins/PoolParty'
			os.system(git_get % new_client)

	if '--load' in sys.argv and len(sys.argv) >= 3:
		completed = True
		if check_pooldeck():
			hostname, ip, pword, pkey = load_credentials(sys.argv[2], DEBUG)
		
	if '--cmd_rmt' in sys.argv and len(sys.argv) > 3:
		completed = True
		if check_pooldeck():
			hostname, ip, pword, pkey = load_credentials(sys.argv[2], DEBUG)
			cmd = utils.arr2chstr(sys.argv[3:])
			utils.ssh_exec(cmd,ip,hostname,pword,True)

	if '--test' in sys.argv and len(sys.argv) >= 3:
		completed = True
		print '[*] Checking connection to %s...' % sys.argv[2]
		if check_pooldeck():
			delta, connected = test_cnx(sys.argv[2])
			if connected:
				print '[*] Successfully connected to %s [%ss Elapsed]' % (sys.argv[2], delta)
			else:
				print '[!] Unable to connect to %s ' % sys.argv[2]

	if '--pool_cnx' in sys.argv:
		completed = True
		test_pool()

	if not completed:
		usage()


if __name__ == '__main__':
	main()
