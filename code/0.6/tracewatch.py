import network
import utils 
import time 
import sys 
import os 



def load_workers():
	nodes = network.get_node_names()
	workers = []
	peers = {}
	# Determine which nodes are available to work
	for n in network.get_node_names():
		name = n.split('/')[-1].split('.')[0]
		h,i,p,m = utils.load_credentials(name, False)
		peers[name] = [h,i,p,m]
		# check if online
		rp = '/home/%s/Documents/PoolParty/code/0.6/hops.txt' % h
		if network.check_connected(h,i,p) and utils.remote_file_exists(h,i,p,rp):
			workers.append(name) 
		else:
			print '%s@%s offline' % (name,i)
	# Now distribute the assignments 
	print '[*] %d Machines Actively Working' % len(workers)
	return workers, peers

def process_hops():
	maximum = 0; n_traces = 0
	for line in utils.swap('hops.txt', True):
		hstr = line.replace('\n','').split(':')[1]
		if hstr != '?':	
			hops = int(line.replace('\n','').split(':')[1])
			if hops > maximum:
				maximum = hops
		n_traces += 1
	return maximum, n_traces


def main():
	# Load Active Worker Machines
	active_nodes, nodes  = load_workers()
	start = time.time()
	running = True
	cycle = 0
	new_scans = 0
	try:
		while running:

			highest = 0; tic = time.time()
			os.system('clear')
			header = '| HOST  |  MAX_HOPS \t|  TOTAL_TRACES |\n '+'='*40
			print '\033[1m'+header+'\033[0m'
			# count local hops first 
			os.system('cp hops.txt oghops.txt')
			local_count, n_local = process_hops()
			if local_count > highest:
				highest = local_count
			d = '| LOCAL | \t%d \t| \t%d \t|' % (local_count, n_local)
			print '\033[1m'+d+'\033[0m'
			counts = {}
			total = n_local
			# Check in with Each one and see what the current best result is
			for worker in active_nodes:
				h,i,p,m = nodes[worker]
				rp =  '/home/%s/Documents/PoolParty/code/0.6/hops.txt' % h
				utils.get_file(rp, h, i ,p, False)
				maxima, ntraced = process_hops()
				counts[worker] = [maxima, ntraced]
				rd = '| %s | \t%d \t| \t%d \t|' % (worker, maxima, ntraced)
				print '\033[1m'+rd+'\033[0m'
				total += ntraced
				if maxima > highest:
					highest = maxima
			dt = time.time()-start
			# put local hops file back
			os.system('mv oghops.txt hops.txt')
			stats = ' MOST HOPS: \033[31m%d\033[0m\033[1m\t TOTAL RUN:\033[31m %d' % (highest, total)
			
			if cycle > 0:
				new_scans = total - new_scans
				ratio = str((new_scans)/(time.time()-tic))
			else:
				new_scans = total
				ratio = '?'
			cycle += 1

			print '\033[1m '+'='*40+'\033[0m'
			print '\033[1m| '+stats+'\033[0m\033[1m |\033[0m'
			print '\033[1m| Time: %ss  [%s/s] |\033[0m' % (dt, ratio)
			print '\033[1m '+'='*40+'\033[0m'
			time.sleep(20)
	except KeyboardInterrupt:
		running = False
		pass


if __name__ == '__main__':
	main()
