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


def parse_logs(logfile, verbose):
	cnxs = []
	arps = {'requests': [], 'replies': []}
	file_in = 'ex.log'
	for line in utils.swap(file_in, False):
		tstamp = line.split(' ')[0]
		try: # IP Protocol Packets 
			IP = line.split('IP')[1].split(' > ')[0]
			if verbose:
				print '[%s]\t%s' % (tstamp, IP)
			cnxs.append([tstamp, IP])
		except IndexError:
			pass
		try: # Find ARP (Requests/Replies)
			ARP = line.split('ARP, ')[1].split(', length')[0]
			if ARP.split(' ')[0]=='Request':
				arps['requests'].append([tstamp, ARP])
				if verbose:
					print '\033[33m\033[1m[%s]\t%s\033[0m' % (tstamp, ARP)
			else:
				arps['replies'].append([tstamp, ARP])
				if verbose:
					print '\033[32m\033[1m[%s]\t%s\033[0m' % (tstamp, ARP)	
		except IndexError:
			pass
	print '%d Network Connections Logged' % len(cnxs)
	print '%d ARP Requests Logged' % len(arps['requests'])
	print '%d ARP Replies Logged' % len(arps['replies'])
	print '[==========================================================]'
	return cnxs, arps

def run(duration,logfile, verbose):
	tic = time.time()	
	packets_read = {}
	
	'''  Start the Network Listener  '''
	p = Thread(target=start_nx_listener, args=('wlan0', logfile))
	p.daemon = True
  	p.start()
  	
	''' Start the Packet Capture Parser Thread AFTER network listener'''
	pool = ThreadPool(processes=1)
	while (time.time()- tic) <= duration:
		dt = time.time()- tic
		try:
			if (dt > 0 and dt % 5 == 0):
				async_read = pool.apply_async(parse_logs, (logfile, verbose))
				nx_traffic = async_read.get() 
		except KeyboardInterrupt:
			print '\033[1m\033[31m[!] KILLED [%ss Elapsed]\033[0m' %\
			 str(time.time()-tic)
	kill_daemon = "ps aux | grep 'tcpdump' | cut -b 10-16 |"\
			"while read proc; do kill -9 $proc > /dev/null>2&1;done"
	os.system(kill_daemon)

if __name__ == '__main__':
	DEBUG = False
	log, date, localtime = create_logfile(DEBUG)
	run(15, log, DEBUG)

