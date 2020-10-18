from threading import Thread
import random
import utils 
import time
import core 
import sys 
import os

def test_cnx(pool_name):
	hostname, ip, pword, pk = core.load_credentials(pool_name, False)
	# Test Command Execution on the remote machine with simple hostname check
	connected = False; start = time.time()
	result = utils.ssh_exec('whoami',ip,hostname,pword,False).replace('\n','')
	if result == hostname:
		connected = True
	# Record how long it took to get a reply from this command
	dt = time.time() - start
	return dt, connected

def multithreaded_cmd_exec(cmd):
	rf = utils.create_random_filename('sh')
	open(rf,'wb').write('#!/bin/bash\n%s\n#EOF' % cmd)
	os.system('bash %s >> /dev/null' % rf)
	os.remove(rf)

def exec_sync_get(pw,rh,ri,sp):
	cmd_data = 'sshpass -p "%s" rsync -avz %s@%s:%s/PoolData/Shares PoolData/' % (pw, rh, ri, sp)
	multithreaded_cmd_exec(cmd_data)

def exec_sync_put(pw, rh, ri, sp):
	cmd_data = 'sshpass -p "%s" rsync -avz PoolData/Shares %s@%s:%s/PoolData/' % (pw, rh, ri, sp)
	multithreaded_cmd_exec(cmd_data)

def synchronize_share_data():
	"""
	This is for folders where all nodes want to have the same files
	In this case, downloading copies from remote nodes.
	"""
	nodes = core.get_node_names()
	creds, latency = core.get_cluster_creds(nodes, True)
	for n in nodes:
		rhost = creds[n][0]
		rip   = creds[n][1]
		pword = creds[n][2]
		if rhost == 'root':
			srcp = '/root/PoolParty/code/0.3'
		else:
			srcp = '/home/%s/PoolParty/code/0.3' % rhost
		print '%s [*] Synchronizing Shares with %s %s %s' % (core.Fb, core.FP, n, core.FE)
		Thread(target=(exec_sync_get), args=(pword, rhost, rip, srcp)).start()

def upload_local_shares():
	"""
	This is for folders where all nodes want to have the same files
	In this case, upload local files to each node
	"""
	nodes = core.get_node_names()
	creds, latency = core.get_cluster_creds(nodes, True)
	for n in nodes:
		rhost = creds[n][0]
		rip   = creds[n][1]
		pword = creds[n][2]
		if rhost == 'root':
			srcp = '/root/PoolParty/code/0.3'
		else:
			srcp = '/home/%s/PoolParty/code/0.3' % rhost
		print '%s [*] Uploading Local Shares to %s %s %s' % (core.Fb, core.FP, n, core.FE)
		Thread(target=(exec_sync_put), args=(pword, rhost, rip, srcp)).start()

def main():

	if '--test' in sys.argv and len(sys.argv)>2:
		username = sys.argv[2]
		if core.check_pooldeck():
			delta, connected = test_cnx(username)
			if connected:
				print '[*] Successfully connected to %s [%ss Elapsed]' % (sys.argv[2], delta)
			else:
				print '[!] Unable to connect to %s ' % sys.argv[2]

	if '--sync-get' in sys.argv:
		synchronize_share_data()

	if '--sync-put' in sys.argv:
		upload_local_shares()

if __name__ == '__main__':
	main()
