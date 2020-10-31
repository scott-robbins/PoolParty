from threading import Thread
import multiprocessing
import numpy as np
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

def command_all(cmd, nodes, verbose):
	pool = multiprocessing.Pool(4)
	results = {}
	for p in nodes:
		hname, ip, pw, pk = core.load_credentials(p, False)
		event = pool.apply_async(func=utils.ssh_exec, args=(cmd, ip, hname, pw, verbose))
		results[p] = event.get(timeout=30)
	return results

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
			srcp = '/root/PoolParty/code/0.4'
		else:
			srcp = '/home/%s/PoolParty/code/0.4' % rhost
		print '%s [*] Uploading Local Shares to %s %s %s' % (core.Fb, core.FP, n, core.FE)
		Thread(target=(exec_sync_put), args=(pword, rhost, rip, srcp)).start()

def test_pool(verbose):
	# Get All Nodes listed in creds
		nodes = list(set(utils.cmd('ls PoolData/Creds/*.creds', False)))
		timing = {}
		# run a connection check for each
		for name in nodes:
			n = name.split('/').pop(-1).split('@')[0]
			ping, cnx = test_cnx(n)
			timing[ping] = n
			if cnx and verbose:
				# color the print out based on reply speed
				if ping <= 0.75:
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.GREEN, ping,utils.FEND)
				if 0.75 < ping < 1.5:
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.YELLOW, ping,utils.FEND)
				if 1.5 < ping :
					print '[*] %s is connected %s[%ss Delay]%s' % (n,utils.BOLD+utils.YELLOW, ping,utils.FEND)
			
		# also calculate fastest
		best_time = np.min(list(set(timing.keys())))
		best_node = timing[best_time]

		# report connectivity
		print '[*] %s is fastest' % best_node
		return best_node, best_time, timing

def show_info(peer_name, verbose):
	hostname, ip, pword, pk = core.load_credentials(peer_name, False)
	poolpath = '/PoolParty/code/0.4'
	if hostname == 'root':
		rpath = '/root' + poolpath
	else:
		rpath = '/home/%s%s' % (hostname,poolpath)
	cmd = ('cd %s;'%rpath) + ' python node.py %s --dump-info ' % peer_name
	result = utils.ssh_exec(cmd, ip, hostname, pword, verbose)
	# Parse result 
	info = {}
	for line in result.split('\n'):
		if len(line.split('\t'))>=2:
			if '-name' in line.replace('\t','').split(':'):
				info['hostname'] = line.split(':')[1].replace('\t','')
			if '-internal ip' in line.replace('\t', '').split(':'):
				info['internal'] = line.split(':')[1].replace('\t', '')
			if '-external ip' in line.replace('\t','').split(':'):
				info['external'] = line.split(':')[1].replace('\t','')
	return result, info

def check_listen():
	listen = True
	if not os.path.isfile(os.getcwd()+'/PoolData/listen.flag'):
		return listen
	else:
		if len(open(os.getcwd()+'/PoolData/listen.flag','rb').read())>0:
			listen = False
	return listen

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

	if '--update-all' in sys.argv:
		command_all('cd ~/PoolParty/code/0.4/; git pull origin', core.get_node_names(), True)

	if '-listen' in sys.argv:
		default=54321
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print '[!!] Unable to create socket'
			exit()
		try:
			s.bind(('0.0.0.0', default))
			s.listen(5)
		except socket.error:
			print '[!!] Conection Broken'
			pass


		while check_listen():
			# accept incoming connection from master
			client, cinfo = s.accept()

			query = client.recv(2048)
			if query == 'KILL':
				open(os.getcwd()+'/PoolData/listen.flag', 'wb').write(query)
				client.send('KILLED')
			client.close()
		# shutdown server socket
		s.close()




if __name__ == '__main__':
	main()
