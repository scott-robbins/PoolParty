from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from threading import Thread
import numpy as np
import random
import warnings
import base64
import socket
import time
import sys 
import os
                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

lowers = ['a','b','c','d','e','f','g','h','i','j',
		  'k','l','m','n','o','p','q','r','s','t',
		  'u','v','w','x','y','z']
uppers = ['A','B','C','D','E','F','G','H','I','J',
		  'K','L','M','N','O','P','Q','R','S','T',
		  'U','V','W','X','Y','Z']
alphas = ['0', '1','2','3','4','5','6','7','8','9']

def swap(filename, destroy):
	data = []
	for line in open(filename, 'rb').readlines():
		data.append(line.decode().replace('\n', ''))
	if destroy:
		os.remove(filename)
	return data

def create_random_filename(ext):
	"""
	Create Random Filename: 
	Creates a valid but random filename. Useful for multithreaded stuff
	when you want to write to disk (but writing to same file will cause issues) 
	
	param: ext (str - file extension)
	return: random_file (str - filename)
	"""
	charpool = []
	for l in lowers: charpool.append(l)
	for u in uppers: charpool.append(u)
	for a in alphas: charpool.append(a)
	basename = ''.join(random.sample(charpool, 6))
	random_file = basename +ext
	return random_file

def arr2str(content):
	"""
	param: 	content		(list - text content in list per line)
	return: result 		(str  - single string of input content with newlines)
	"""
	result = ''
	for element in content:
		if len(element) > 1:
			result += (element + '\n')
		else:
			result += element
	return result

def arr2chr(content):
	"""
	param: 	content		(list - text content in list per word)
	return: result 		(str  - single string of input content)
	"""
	result = ''
	for element in content:
		result += (element + ' ')
	return result

def cmd(command, verbose):
	tmp = create_random_filename('.sh')
	tmp2 = create_random_filename('.txt')
	data = '#!/bin/bash\n%s\n#EOF' % command
	open(tmp, 'w').write(data)
	os.system('bash %s >> %s' % (tmp,tmp2))
	os.remove(tmp)
	if verbose:	
		os.system('cat %s' % tmp2)
	return swap(tmp2, True)

def get_ext_ip():
	return cmd('curl -s https://api.ipify.org',False).pop()

def get_internal_addr():
	addrs = cmd('hostname -I',False).pop().split(' ')
	addrs.pop(-1)
	return addrs

def ssh_exec(c, ip_address, uname, password, verbose):
	comm = 'sshpass -p "%s" ssh %s@%s %s' % (password, uname, ip_address, c)
	return cmd(comm, verbose)
	
def create_password():
	matched = False
	password = ''
	attempts =  0
	while not matched and attempts < 3:
		cmd = "#!/bin/bash\n echo 'Enter Password:'; read -s PASS; echo $PASS >> cmd.txt\n#EOF"
		open('tmp.sh','wb').write(cmd.encode())
		os.system('bash tmp.sh; rm tmp.sh')
		password = swap('cmd.txt', True).pop()
		# Double Check it twice before creating 
		cmd2 = "#!/bin/bash\n echo 'Re-Enter Password:'; read -s PASS; echo $PASS >> cmd.txt\n#EOF"
		open('tmp.sh','wb').write(cmd2.encode())
		os.system('bash tmp.sh; rm tmp.sh')
		password_check = swap('cmd.txt', True).pop()
		if password == password_check:
			print( '[*] Username and Password Created')
			matched = True
		elif (len(password) > 7):
			print('[x] Password must be longer than 7 Characters!')
		else:
			print('[X] The two password entries did not match!')
		attempts += 1
	return matched, password

def create_keys(creds):
	# Create this peers private key
	success = False
	key = RSA.generate(2048)
	private_key = key.exportKey()
	public_key = key.publickey()
	with open(os.getcwd()+'/PoolData/Creds/%s.pem' % creds['pname'],'wb') as file_out:
		file_out.write(key.exportKey())
	file_out.close()
	# Now Encrypt their Network Info/Creds with their public key
	cipher_rsa = PKCS1_OAEP.new(public_key)
	cred_dat = '%s@%s:%s\n' % (creds['hname'],creds['IP'],creds['pword'])
	cred_dat += 'MAC:%s' % creds['MAC']
	enc_data = cipher_rsa.encrypt(cred_dat.encode())
	fname = creds['name']
	with open(os.getcwd()+'/PoolData/Creds/%s' % fname, 'wb') as file_out:
		file_out.write(enc_data)
	file_out.close()
	print ('[*] Credentials created for %s' % creds['pname'])
	return success

def load_credentials(peername, verbose):
	found = False
	key_name = peername+'.pem'
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		print('[!!] Missing Credential Folder')
	if not os.path.isfile(os.getcwd()+'/PoolData/Creds/%s' % key_name):
		print('[!!] Credentials not found')
	
	for name in os.listdir('PoolData/Creds'):
		if len(name.split('@'))==2:
			if peername == name.split('@')[0]:
				if verbose:
					print('[*] Found Credentials for %s' % peername)
				
				host = name.split('@')[1].split('.creds')[0]
				found = True
	if not found:
		print('[!!] Unable to find username %s' % peername)
		return '','','',''

	cred_file  = os.getcwd()+'/PoolData/Creds/'+peername+'@'+host+'.creds'
	with open(os.getcwd()+'/PoolData/Creds/%s' % key_name, 'rb') as key_file:
		private_key = RSA.importKey(key_file.read().decode())
	with open(cred_file,'rb') as cfile:
		enc_dat = cfile.read()
	# Now decrypt them with private key
	raw_creds = PKCS1_OAEP.new(private_key).decrypt(enc_dat).decode()
	hostname = raw_creds.split('@')[0]
	ip_addr = raw_creds.split('@')[1].split(':')[0]
	password = raw_creds.split(':')[1].replace('\n','').split('MAC')[0]
	macaddr = raw_creds.split('\n')[1].split('MAC:')[1]
	return hostname, ip_addr, password, macaddr

def create_tcp_listener(port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		pass
		print('[!!] Unable to create socket on 0.0.0.0:%d' % port)
		return []
	try:
		s.bind(('0.0.0.0', port))
		s.listen(5)
	except socket.error:
		pass
		print('[!!] Connection Broken on 0.0.0.0:%d' % port)
		return []
	# Return the listening server socket on designated port
	return s

def remote_file_exists(host, ip , passwd, path_to_file):
	c = '[ ! -e %s ]; echo $?' % path_to_file
	return int(ssh_exec(c, ip, host, passwd, False).pop())

def get_file(remote_file_path, host, ip, passwd, verbose):
	c = 'sshpass -p "%s" sftp %s@%s:%s' % (passwd, host, ip, remote_file_path)
	local_copy = remote_file_path.split('/')[-1]
	reply = cmd(c, verbose)
	if verbose and os.path.isfile(local_copy):
		print('[*] %d bytes transferred' % os.path.getsize(local_copy))
	return reply

def put_file(local_file_path, remote_destination, host, ip, passwd, verbose):
	c = 'sshpass -p "%s" sftp %s@%s:%s <<< $'% (passwd, host, ip,remote_destination)
	c += "'put %s'" % local_file_path
	reply = cmd(c, False)
	if verbose and os.path.isfile(local_file_path):
		print('[*] %d bytes transferred' % os.path.getsize(local_file_path))
	return reply

def get_node_list():
	names = []
	for i in os.listdir(os.getcwd()+'/PoolData/Creds'):
		names.append(i.split('/')[-1].split('.')[0].split('@')[0])
	return list(set(names))

def check_node_reachable(ip):
	c = 'ping -c 2 %s >> /dev/null; echo $?' % ip
	connected = False
	try:
		status = int(cmd(c,False).pop())
	except:
		pass
	if status == 0:
		connected = True
	return status

def get_fresh_macs():
	data = []
	os.system("nmap -T5 192.168.0/24")
	for line in cmd('arp -a',False):
		ip = line.split(')')[0].split('(')[1]
		mac = line.split(' at ')[1].split(' ')[0]
		data.append([ip, mac])
	return data 