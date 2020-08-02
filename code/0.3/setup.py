from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
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

	if debug:
		print 'hostname: %s' % host
		print 'IP Address: %s' % ip_addr
		print 'Password: %s' % password

	return host, ip_addr, password, private_key

def main():
	DEBUG = True
	if '-add' in sys.argv:
		add_client_cmdline()

	if '-load' in sys.argv and len(sys.argv) >= 3:
		hostname, ip, pword, pkey = load_credentials(sys.argv[2], DEBUG)
		

if __name__ == '__main__':
	main()
