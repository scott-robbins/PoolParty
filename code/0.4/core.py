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

# Any of these [3xm with [4xm will highlight in that color instead
Fb = '\033[1m'	# Bold
Fi = '\033[3m'	# Italic
FR = '\033[31m'	# Red
FG = '\033[32m'	# Green
FO = '\033[33m'	# Orange
FB = '\033[34m'	# Blue
FP = '\033[35m'	# Purple
FC = '\033[36m' # Cyan
FE = '\033[0m' 	# End 

def get_cluster_creds(user_nodes, check_cnx):
	"""
	Also tests connection to nodes...
	"""
	node_creds = {}
	ping = {}
	# Get all the credentials for each node 
	for username in user_nodes:
		hname, ip, pword, pkey = load_credentials(username, False)
		node_creds[username] = [hname, ip, pword]
		if check_cnx:
			start = time.time()
			result = utils.ssh_exec('whoami', ip, hname, pword, False).replace('\n','')
			stop = time.time()
			if result == hname:
				p = float(stop-start)
				ping[username] = p

				# color the print out based on reply speed
				if p <= 0.55:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,Fb+FG, p, FE)
				if 0.55 < p < 1.25:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,Fb+FO, p, FE)
				if 1.25 <= p:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,Fb+FR, p, FE)
	return node_creds, ping

def get_node_names():
	ns = []
	for n in list(set(utils.cmd('ls PoolData/Creds/*.creds',False))):
		ns.append(n.split('@')[0].split('/')[-1])
	return ns 

def create_credentials_interactive():
	# Make sure password folders are present
	check_folders()
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
	# Return the Username and Password registereds
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

def create_credentials_from_file(credconfig):
	'''
	credetial config file should be the four following lines: 
	
	IPAddress=10.10.10.10
	Password=YourPassword
	Username=computerhost
	Hostname=PartyPanda
	'''
	# Make sure password folders are present
	check_folders()
	pword = ''; ip_addr = ''
	for line in utils.swap(credconfig, True):
		field = line.split('=')[0]
		value = line.split('=')[1]
		if field == 'Password':
			pword = value
		if field == 'IPAddress':
			ip_addr = value
		if field == 'Username':
			uname = value
		if field == 'Hostname':
			hname = value
			newcred = '%s.pem' % uname
			newcredfile = os.getcwd()+'/PoolData/Creds/%s.pem' % uname
			existing = os.listdir(os.getcwd()+'/PoolData/Creds/')

			if newcredfile not in existing and len(pword)>1 and len(ip_addr)>1:
				# Save Them, Encrypted with private key (also saved)
				key = RSA.generate(2048)
				private_key = key.exportKey()
				public_key = key.publickey()
				file_out = open(os.getcwd()+"/PoolData/Creds/%s.pem" % uname, "wb")
				file_out.write(key.exportKey('PEM'))
				file_out.close()
				# Encrypt the session key with the public RSA key
				cipher_rsa = PKCS1_OAEP.new(public_key)
				cred_file_dat = b'%s@%s:%s' % (uname, ip_addr, pword)
				enc_cred_data = cipher_rsa.encrypt(cred_file_dat)
				fname = '%s@%s' % (uname, hname)
				open(os.getcwd()+'/PoolData/Creds/%s.creds' % fname, 'wb').write(enc_cred_data)
				print '%s[*] Credentials created for %s %s %s' % (Fb, FG, uname, FE)
			else:
				print 'Cannot Create Credentials for %s.\n Username already exists' % value
				exit()
	return uname, pword

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

def usage():
	print '[!!] Incorrect usage [!!]\n'
	print '$ python setup.py <opt> <args>\n'
	print 'Valid options are:'
	info = {'--add': 'Add peer to network',
			'--load': 'Load Credentials for a node',
			'--add_configured': 'Add peer using config file'}
	for o in info.keys():
		print '\t-%s    \t(%s)' % (o, info[o])

def check_folders():
	if not os.path.isdir(os.getcwd()+'/PoolData/'):
		os.mkdir('PoolData')
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		os.mkdir(os.getcwd()+'/PoolData/Creds')

def main():
	completed = False
	DEBUG = False
	if '-vv' in sys.argv:
		DEBUG = True
	
	# Create User from commandline
	if '--add' in sys.argv:
		completed = True
		new_client = create_credentials_interactive()
	
	if '--add_configured' in sys.argv and len(sys.argv) >= 2:
		completed = True
		conf = sys.argv[2]
		new_client = create_credentials_from_file(conf)

	# Load Credentials
	if '--load' in sys.argv and len(sys.argv) >= 3:
		completed = True
		if check_pooldeck():
			hostname, ip, pword, pkey = load_credentials(sys.argv[2], DEBUG)
		else:
			print '[!] No credentials found'

	# If no actions were taken show usage message
	if not completed:
		usage()

if __name__ == '__main__':
	main()
