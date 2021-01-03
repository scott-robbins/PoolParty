import multiprocessing
import network
import random
import utils
import sys 
import os

def trace(addr, verbose):
	hops = {}
	f = utils.create_random_filename('.txt')
	c = 'traceroute -m65 %s >> %s' % (addr, f)
	os.system(c)
	i = 0
	for l in utils.swap(f,True):
		
		if i > 0:
			h =l.replace('\n','').split(' ')[3].replace('(','').replace(')','')
			hops[i] = h
		i += 1
	# starting from the end, remove *** hops
	N = len(hops.keys())
	nH = 0
	for n in range(N,0,-1):
		if hops[n] == '*':
			del hops[n]
		else:
			nH = n
			break
	return hops, nH

def ip_block(a,b):
	addrs = []
	for i in range(a,b,1):
		for j in range(1,255,1):
			for k in range(1,255):
				a = '%s.%s.%d.1' % (i,j,k)
				print a
				open('ip_space.txt', 'a').write('%s\n' % a)


def monitor_progress(hosts):
	watching = True
	try:
		while watching:
			# Look at Local hops.txt
			# Look at the hops.txt of each worker
			for n in hosts.keys():
				h,i,p,m = hosts[n]
				rpath = '/home/%s/Documents/PoolParty/code/0.6/hops.txt' % H


	except KeyboardInterrupt:
		watching = False
		pass

def main():
	if '-gen' in sys.argv:
		A = int(sys.argv[2])
		B = int(sys.argv[3])
		ip_block(A, B)

	# Create a way to run this distributed from python
	elif '-multi-setup' in sys.argv:
		import network
		workers = []
		peers = {}
		# Determine which nodes are available to work
		for n in network.get_node_names():
			name = n.split('/')[-1].split('.')[0]
			h,i,p,m = utils.load_credentials(name, False)
			peers[name] = [h,i,p,m]
			# check if online
			if network.check_connected(h,i,p):
				workers.append(name) 
			else:
				print '%s@%s offline' % (name,i)

		# Now distribute the assignments 
		print '[*] %d Workers Available' % len(workers)
		for w in workers:
			# give them the latest copy of this program
			H,I,P,M = peers[w]
			rpath = '/home/%s/Documents/PoolParty/code/0.6/' % H
			if utils.remote_file_exists(H,I,P,rpath+'trace.py'):
				utils.ssh_exec('rm %strace.py' % rpath,I,H,P,False)
			utils.put_file('trace.py',rpath,H,I,P,False)
			# Now give them a ip_space.txt file and a script to run trace.py
			utils.ssh_exec('rm %shops.txt' % rpath,I,H,P,True)
			# c = 'cd %s; python trace.py 0>&-' % rpath
			# put this in a .sh script and transfer, then execute
			# utils.ssh_exec('cd %s; python trace.py 0>&-' % rpath,H,I,P,False)


	elif '-multi-view' in sys.argv:
		import tracewatch
		print('[*] Monitoring Traces...')


	else:
		ips = list(utils.swap('ip_space.txt', False))
		if not os.path.isfile(os.getcwd()+'/hops.txt'):
			os.system('touch hops.txt')
		random.shuffle(ips)
		pool = multiprocessing.Pool(10)
		for ip in ips:
			try:
				event = pool.apply_async(func=trace, args=(ip,False))
				hopdata, nhops = event.get(timeout=60)
				print ' - %d hops to %s' % (nhops, ip)
				open('hops.txt', 'a').write('%s:%d\n' % (ip, nhops))
			except multiprocessing.TimeoutError:
				open('hops.txt', 'a').write('%s:?\n' % ip)
				pass

if __name__ == '__main__':
	main()
