from multiprocessing.pool import ThreadPool
from threading import Thread
import utils 
import time 
import sys 
import os


def create_logfile(verbose):
	date, localtime = utils.create_timestamp()
	log_data = '< LAN MONITOR STARTED > \t%s - %s' % (date, localtime)
	log_date = date.split('/')[0]+date.split('/')[1]+date.split('/')[2] 
	log_time = localtime.split(':')[0]+localtime.split(':')[1] +\
	 		   localtime.split(':')[2]
	log_name = 'LOG_' + log_date + '_' + log_time + '.txt'
	open(log_name,'w').write(log_data+'\n')
	if verbose:
		print '\033[1m'+log_data+'\033[0m'
	return log_name, date, localtime 


def start_nx_listener(iface, logfile):
	cmd = 'tcpdump -i %s >> %s' % (iface, logfile)
	print 'Executing: %s' % cmd
	os.system(cmd)


def parse_logs(logfile):
	nx_packets = {}
	if not os.path.isfile(logfile):
		print '\033[1m\033[31m[!] Logfile Missing!!\033[0m'
		exit()
	for line in utils.swap(logfile, False):
		print line
	return nx_packets
	

def run(duration,logfile):
	tic = time.time()	
	packets_read = {}
	
	'''  Start the Network Listener  '''
	p = Thread(target=start_nx_listener, args=('wlan0', logfile))
	p.daemon = True
  	p.start()
  	
	''' '''
	pool = ThreadPool(processes=1)
	while (time.time()- tic) <= duration:
		dt = time.time()- tic
		try:
			if (dt > 0 and dt % 5 == 0):
				async_read = pool.apply_async(parse_logs, (logfile,))
				nx_traffic = async_read.get() 
		except KeyboardInterrupt:
			print '\033[1m\033[31m[!] KILLED [%ss Elapsed]\033[0m' %\
			 str(time.time()-tic)
	kill_daemon = "ps aux | grep 'tcpdump' | cut -b 10-16 |"\
				  " while read proc; do kill -9 $proc > /dev/null; done"
	os.system(kill_daemon)

if __name__ == '__main__':
	DEBUG = True
	log, date, localtime = create_logfile(DEBUG)
	run(15, log)

