from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from threading import Thread
import numpy as np
try:
	import paramiko
	MIKO = True
except ImportError:
	# print '[!!] Cannot use Paramiko'
	MIKO = False
import random
import warnings
import base64
import socket
import time
import sys 
import os
                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

FEND = '\033[0m'
BOLD = '\033[1m'
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
YELLOW = '\033[33m'

lowers = ['a','b','c','d','e','f','g','h','i','j',
		  'k','l','m','n','o','p','q','r','s','t',
		  'u','v','w','x','y','z']
uppers = ['A','B','C','D','E','F','G','H','I','J',
		  'K','L','M','N','O','P','Q','R','S','T',
		  'U','V','W','X','Y','Z']
alphas = ['0', '1','2','3','4','5','6','7','8','9']

def create_random_filename(ext):
	charpool = []
	for l in lowers: charpool.append(l)
	for u in uppers: charpool.append(u)
	for a in alphas: charpool.append(a)
	basename = ''.join(random.sample(charpool, 6))
	random_file = basename +ext
	return random_file

def swap(filename, destroy):
	data = []
	for line in open(filename, 'rb').readlines():
		data.append(line.replace('\n', ''))
	if destroy:
		os.remove(filename)
	return data

def arr2str(content):
	result = ''
	for element in content:
		result += element + '\n'
	return result

def arr2chstr(content):
	result = ''
	for element in content:
		result += element + ' '
	return result

def get_sha256_sum(file_name, verbose):
    if len(file_name.split("'"))>=2:
        file_name = ("{!r:}".format(file_name))
        os.system("sha256sum "+file_name + ' >> out.txt')
    else:
        os.system("sha256sum '%s' >> out.txt" % file_name)
        sum_data = swap('out.txt', True).pop().split(' ')[0]
    if verbose:
        print sum_data

    return sum_data

def crawl_dir(file_path, doHash, verbose):
    directory = {'dir': [], 'file': []}
    hashes = {}
    folders = [file_path]
    while len(folders) > 0:
        direct = folders.pop()
        if verbose:
            print 'Exploring %s' % direct
        try:
            for item in os.listdir(direct):
                if os.path.isfile(direct + '/' + item):
                    file_name = direct + "/" + item
                    directory['file'].append(file_name)
                    if doHash:
                        hashes['"' + file_name.replace('"','') + '"'] = get_sha256_sum(file_name, False)
                    if verbose:
                        print '\033[3m- %s Added to Shared Folder\033[0m' % file_name
                else:
                    directory['dir'].append(direct + '/' + item)
                    folders.append(direct + '/' + item)
        except OSError:
            pass
    return directory, hashes

def get_ext_ip():
	return cmd('curl -s https://api.ipify.org',False).pop()

def get_internal_addr():
	addrs = cmd('hostname -I',False).pop().split(' ')
	addrs.pop(-1)
	return addrs

def create_timestamp():
    date = time.localtime(time.time())
    mo = str(date.tm_mon)
    day = str(date.tm_mday)
    yr = str(date.tm_year)

    hr = str(date.tm_hour)
    min = str(date.tm_min)
    sec = str(date.tm_sec)

    date = mo + '/' + day + '/' + yr
    timestamp = hr + ':' + min + ':' + sec
    return date, timestamp

def load_credentials(filepath):
	if filepath == 'Server':
		filepath = os.getcwd()+'/Creds/Server@root.creds'
	username = ''
	ip = ''
	passwd = ''
	lines = swap(filepath, False)
	try:
		passwd = lines[0].split(' ')[0]
		username = lines[1].split('@')[0]
		ip = lines[1].split('@')[1]
	except IndexError:
		pass
	return username, ip, passwd

def cmd(command, verbose):
	os.system('%s >> cmd.txt' % command)
	if verbose:	
		os.system('cat cmd.txt')
	return swap('cmd.txt', True)

def ssh_exec(cmd, ip_address, uname, password, verbose):
	client = paramiko.SSHClient()	# TODO: Add no Miko error handling
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
	reply = ''
	
	try:
		client.connect(ip_address, username=uname, password=password)
		ssh_session = client.get_transport().open_session()
		if ssh_session.active:
			ssh_session.exec_command(cmd)
			reply = ssh_session.recv(100000)
		if verbose:
			print '$ %s\n$ %s' % (cmd,reply)
			
	except paramiko.SSHException:
		pass
	except paramiko.ssh_exception.NoValidConnectionsError:
		pass
	return reply

def ssh_exec_noreply(cmd, ip_address, uname, password):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
	executed = False

	try:	# actually connect and execute command
		client.connect(ip_address, username=uname, password=password)
		ssh_session = client.get_transport().open_session()
		if ssh_session.active:
			ssh_session.exec_command(cmd)
			executed = True
	except paramiko.SSHException:
		pass
	except paramiko.ssh_exception.NoValidConnectionsError:
		pass
	return executed

def ssh_get_file(r_path, rmt_file, ip, uname, passwd):
	# TODO: Add no Miko error handling
	cmd = 'sshpass -p "%s" sftp %s@%s:%s/%s' % (passwd, uname, ip, r_path,rmt_file)
	os.system(cmd)
	return True

def ssh_get_file_del(r_path, rmt_file, ip, uname, passwd):
	# Function for getting file and deleting remote copy in one command
	cmd_get = 'sshpass -p "%s" sftp %s@%s:%s/%s; ' % (passwd, uname, ip, r_path,rmt_file)
	cmd_del_a = 'sshpass -p "%s" ssh %s@%s ' % (passwd, uname, ip)
	cmd_del_b = "'rm %s/%s'" % (r_path, rmt_file)
	cmd_full = cmd_get + cmd_del_a + cmd_del_b
	deleted = False
	try:
		os.system(cmd_full)
		deleted = True
	except OSError:
		pass
	return deleted	

def ssh_put_file(localfile, rpath, ip, uname, password):
	# TODO: Add no Miko error handling
	cmd1 = 'sshpass -p "%s" sftp %s@%s:%s' % (password,uname,ip,rpath)
	cmd2 = " <<< $'put %s'" % (localfile)
	getreq = cmd1+cmd2
	# If I randomize file names, I should be able to multithread this function?
	token = base64.b64encode(get_random_bytes(4)).replace('/','Y')
	fname = 'tmp%s.sh' % token
	open(fname,'wb').write('#!/bin/bash\n%s\n#EOF'%getreq)
	os.system('bash %s >> /dev/null' % fname)
	os.remove(fname)
	return True

# #################### CRYPTOGRAPHIC LAMBDA FUNCTIONS #################### #
BLOCK_SIZE = 16     # the block size for the cipher object; must be 16 per FIPS-197
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING        # pad text to be encrypted
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))            # encrypt with AES
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
# ##############  ###### ~ LAMBDA DEFINITIONS END ~ ######  ############## #


def start_listener(port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('0.0.0.0', port))
		s.listen(5)
	except socket.error:
		print '[!!] Error Creating Listener'
		return []
	return s

def create_tcp_socket(verbose):
	s = []
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		if verbose:
			print '!! Unable to create socket'
		pass
	return s 

def execute_python_script(rmt_file_path, rmt_file, ip, uname, password, verbose):
	# Create a temp script to execute the python on the remote machine
	script = '#!/bin/bash\ncd %s\npython %s \n' % (rmt_file_path, rmt_file)
	script += 'rm -- "$0"\n#EOF\n' # make the script self deleting for easier
	open('tmpsc.sh','wb').write(script)
	ssh_put_file('tmpsc.sh', '%s'%rmt_file_path, ip, uname, password)
	os.remove('tmpsc.sh')
	# execute the script and retrieve the result (if any needs to be grabbed)
	c = 'bash %s/tmpsc.sh' % rmt_file_path
	result = ssh_exec(c ,ip,uname,password, True)
	if verbose:
		print result
	return result

def refresh_peers():
	if not os.path.isdir(os.getcwd()+'/PoolData/NX'):
		print '[!!] No NX Folder Found'
		os.mkdir(os.getcwd()+'/PoolData/NX')
		return
	if os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
		os.remove(os.getcwd()+'/PoolData/NX/peerlist.txt')
	content = ''
	for name in cmd('ls PoolData/Creds/*.pem', False):
		content += name.split('/')[-1].split('.pem')[0]+'\n'
	open(os.getcwd()+'/PoolData/NX/peerlist.txt','wb').write(content)

# ############################## RSYNC OPERATIONS ############################## #

